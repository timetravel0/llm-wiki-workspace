from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


class HttpRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_env() -> None:
    _load_env_file(ROOT / ".env")
    load_shared = os.getenv("WIKI_LOAD_SHARED_ENV", "0").strip().lower() in {"1", "true", "yes", "on"}
    if load_shared:
        shared_path = os.getenv("WIKI_SHARED_ENV_PATH", "../.env.shared")
        _load_env_file((ROOT / shared_path).resolve())


def _allow_internal_network() -> bool:
    return os.getenv("ALLOW_INTERNAL_NETWORK", "0").strip().lower() in {"1", "true", "yes", "on"}


def _allowed_hosts() -> set[str]:
    return {
        host.strip().lower()
        for host in os.getenv("INTERNAL_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
        if host.strip()
    }


def require_localhost(url: str, label: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"{label} deve essere un URL http(s)")
    if not _allow_internal_network() and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError(f"{label} deve puntare a localhost")
    if _allow_internal_network() and parsed.hostname and parsed.hostname.lower() not in _allowed_hosts():
        raise ValueError(f"{label} deve puntare a un host interno consentito")
    return url.rstrip("/")


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    body = None
    request_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HttpRequestError(f"{method} {url} failed with {exc.code}: {detail}", exc.code) from exc
    except urllib.error.URLError as exc:
        raise HttpRequestError(f"{method} {url} failed: {exc.reason}") from exc


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---", 4)
    if end == -1:
        return {}, content
    raw = content[4:end]
    body = content[end + 4 :].lstrip("\r\n")
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.lower() in {"true", "false"}:
            data[key] = value.lower() == "true"
        elif value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip('"').strip("'") for item in value[1:-1].split(",")]
            data[key] = [item for item in items if item]
        else:
            data[key] = value.strip('"').strip("'")
    return data, body


def should_publish(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    if "archive" in parts or "inbox" in parts:
        return False
    return path.suffix.lower() in {".md", ".txt"}


def collect_pages(wikis_root: Path, wiki_slug: str | None) -> list[dict[str, Any]]:
    if wiki_slug:
        wiki_dirs = [wikis_root / wiki_slug]
    else:
        wiki_dirs = [path for path in wikis_root.iterdir() if path.is_dir()] if wikis_root.exists() else []

    pages: list[dict[str, Any]] = []
    for wiki_dir in wiki_dirs:
        wiki_content_dir = wiki_dir / "wiki"
        if not wiki_content_dir.exists():
            continue
        slug = wiki_dir.name
        for path in sorted(wiki_content_dir.rglob("*")):
            if not path.is_file() or not should_publish(path):
                continue
            content = path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)
            if frontmatter.get("rag_index") is not True:
                continue
            rel = path.relative_to(ROOT).as_posix()
            wiki_rel = path.relative_to(wiki_dir).as_posix()
            pages.append(
                {
                    "path": rel,
                    "content": content,
                    "metadata": {
                        "source": "llm-wiki-workspace",
                        "wiki_slug": slug,
                        "wiki_relative_path": wiki_rel,
                        "title": frontmatter.get("title") or path.stem,
                        "type": frontmatter.get("type") or "page",
                        "tags": frontmatter.get("tags") or [],
                        "rag_scope": frontmatter.get("rag_scope") or "",
                        "content_hash": content_hash(content),
                    },
                }
            )
    return pages


def publish_pages(pages: list[dict[str, Any]], *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "found": len(pages),
            "created": len(pages),
            "updated": 0,
            "deleted_replaced": 0,
            "skipped": 0,
            "dry_run": True,
        }

    wiki_url = require_localhost(os.getenv("WIKI_SERVICE_URL", "http://127.0.0.1:8200"), "WIKI_SERVICE_URL")
    token = os.getenv("INTERNAL_API_TOKEN", "")
    if not token:
        raise RuntimeError("INTERNAL_API_TOKEN non impostato")
    headers = {"Authorization": f"Bearer {token}"}
    existing = request_json("GET", f"{wiki_url}/api/v1/documents", headers=headers).get("documents", [])
    by_path = {item.get("path"): item for item in existing if item.get("path")}

    created = 0
    updated = 0
    skipped = 0
    deleted = 0
    to_create: list[dict[str, Any]] = []
    for page in pages:
        current = by_path.get(page["path"])
        if current and current.get("content_hash") == page["metadata"]["content_hash"]:
            skipped += 1
            continue
        if current:
            updated += 1
            deleted += 1
            if not dry_run:
                request_json("DELETE", f"{wiki_url}/api/v1/documents/{current['id']}", headers=headers)
        else:
            created += 1
        to_create.append(page)

    if to_create and not dry_run:
        for page in to_create:
            request_json(
                "POST",
                f"{wiki_url}/api/v1/documents",
                headers=headers,
                payload={
                    "files": [{"path": page["path"], "content": page["content"]}],
                    "metadata": page["metadata"],
                },
            )
    return {
        "found": len(pages),
        "created": created,
        "updated": updated,
        "deleted_replaced": deleted,
        "skipped": skipped,
        "dry_run": dry_run,
    }


def sync_simple_rag(*, wiki_slug: str | None, dry_run: bool, required: bool) -> dict[str, Any]:
    simple_rag_url = require_localhost(os.getenv("SIMPLE_RAG_URL", "http://127.0.0.1:8000"), "SIMPLE_RAG_URL")
    api_token = os.getenv("API_AUTH_TOKEN", "")
    if not api_token:
        result = {"skipped": True, "reason": "API_AUTH_TOKEN non impostato"}
        if required:
            raise RuntimeError(result["reason"])
        return result
    if dry_run:
        return {"skipped": True, "reason": "dry_run"}
    headers = {"x-api-key": api_token}
    try:
        result = request_json(
            "POST",
            f"{simple_rag_url}/api/v1/sync/wiki-service",
            headers=headers,
            payload={},
            timeout=60.0,
        )
        result["sync_method"] = "wiki-service"
        return result
    except HttpRequestError as exc:
        if exc.status_code != 404:
            raise
        result = request_json(
            "POST",
            f"{simple_rag_url}/api/v1/ingest/wiki/sync",
            headers=headers,
            payload={
                "wiki_root": str(ROOT),
                "wiki_slug": wiki_slug,
                "collection": "documentation",
                "namespace": "default",
                "incremental": True,
            },
            timeout=120.0,
        )
        result["sync_method"] = "filesystem-fallback"
        result["fallback_reason"] = "/api/v1/sync/wiki-service returned 404"
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish native wiki pages to the integrated local platform.")
    parser.add_argument("--wiki-slug", default=None, help="Publish only one wiki slug.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be published without writing.")
    parser.add_argument(
        "--no-simple-rag-sync",
        action="store_true",
        help="Publish to Wiki Service only, without calling simple_rag sync.",
    )
    parser.add_argument(
        "--require-simple-rag-sync",
        action="store_true",
        help="Fail if simple_rag sync cannot be completed.",
    )
    args = parser.parse_args()

    load_env()
    pages = collect_pages(ROOT / "wikis", args.wiki_slug)
    publish_result = publish_pages(pages, dry_run=args.dry_run)
    result: dict[str, Any] = {"wiki_service": publish_result}
    if not args.no_simple_rag_sync:
        result["simple_rag_sync"] = sync_simple_rag(
            wiki_slug=args.wiki_slug,
            dry_run=args.dry_run,
            required=args.require_simple_rag_sync,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
