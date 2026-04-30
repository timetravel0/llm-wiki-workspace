from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False, encoding="utf-8-sig")

WIKI_LOAD_SHARED_ENV = os.getenv("WIKI_LOAD_SHARED_ENV", "0").strip().lower() in {"1", "true", "yes", "on"}
WIKI_SHARED_ENV_PATH = os.getenv("WIKI_SHARED_ENV_PATH", "../.env.shared")
if WIKI_LOAD_SHARED_ENV:
    load_dotenv(dotenv_path=(BASE_DIR / WIKI_SHARED_ENV_PATH).resolve(), override=False, encoding="utf-8-sig")

app = FastAPI(title="Wiki Service", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

DOCS_DIR = Path(os.getenv("WIKI_DOCS_DIR", "./docs")).resolve()
INTERNAL_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")
ALLOWED_EXTENSIONS = {".md", ".txt"}
MAX_FILE_SIZE = int(os.getenv("WIKI_MAX_FILE_SIZE_BYTES", "1048576"))
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}


class DocumentFile(BaseModel):
    path: str = Field(min_length=1, max_length=240)
    content: str

    @field_validator("path")
    @classmethod
    def valid_path(cls, value: str) -> str:
        clean = value.replace("\\", "/").strip()
        if clean.startswith("/") or ".." in Path(clean).parts:
            raise ValueError("path non valido")
        suffix = Path(clean).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"estensione non ammessa: {suffix}")
        return clean


class CreateDocumentsRequest(BaseModel):
    files: list[DocumentFile] = Field(min_length=1, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateDocumentRequest(BaseModel):
    content: str = Field(min_length=1)
    message: str = ""
    author: str = "unknown"


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _content_size(content: str) -> int:
    return len(content.encode("utf-8"))


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _verify_local(request: Request) -> None:
    host = request.client.host if request.client else ""
    if host == "testclient" and os.getenv("PYTEST_CURRENT_TEST"):
        return
    if host not in LOCAL_HOSTS:
        raise HTTPException(status_code=403, detail="localhost required")


def verify_token(request: Request) -> None:
    _verify_local(request)
    auth = request.headers.get("Authorization", "")
    if not INTERNAL_TOKEN or not auth.startswith("Bearer ") or auth[7:] != INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")


def _doc_id(path: str, content: str) -> str:
    return hashlib.sha256(f"{path}\0{content}".encode("utf-8")).hexdigest()[:16]


def _validate_item_id(doc_id: str) -> str:
    if not doc_id.isalnum() or len(doc_id) > 64:
        raise HTTPException(status_code=400, detail="doc_id non valido")
    return doc_id


def _doc_dir(doc_id: str) -> Path:
    _validate_item_id(doc_id)
    return DOCS_DIR / "_store" / doc_id


def _load_index() -> dict[str, Any]:
    return _read_json(DOCS_DIR / "index.json", default={}) or {}


def _save_index(index: dict[str, Any]) -> None:
    _write_json(DOCS_DIR / "index.json", index)


def _audit(event: str, item_id: str, metadata: dict[str, Any]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"ts": _now(), "event": event, "id": item_id, "metadata": metadata}, ensure_ascii=False)
    with (DOCS_DIR / "audit.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _read_meta(doc_id: str) -> dict[str, Any]:
    meta_path = _doc_dir(doc_id) / "meta.json"
    meta = _read_json(meta_path)
    if not meta:
        raise HTTPException(status_code=404, detail="document not found")
    return dict(meta)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "llm_wiki_workspace"}


@app.post("/api/v1/documents", dependencies=[Depends(verify_token)])
async def create_documents(payload: CreateDocumentsRequest) -> dict[str, Any]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    index = _load_index()
    ids: list[str] = []
    for item in payload.files:
        size = _content_size(item.content)
        if size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="file troppo grande")
        item_id = _doc_id(item.path, item.content)
        folder = _doc_dir(item_id)
        folder.mkdir(parents=True, exist_ok=True)
        content_path = folder / "content.md"
        meta = {
            "id": item_id,
            "path": item.path,
            "section": payload.metadata.get("section", Path(item.path).parts[0] if Path(item.path).parts else ""),
            "tags": list(payload.metadata.get("tags", []) or []),
            "metadata": payload.metadata,
            "created_at": _now(),
            "content_hash": _content_hash(item.content),
            "size_bytes": size,
            "content_file": content_path.name,
        }
        content_path.write_text(item.content, encoding="utf-8")
        _write_json(folder / "meta.json", meta)
        index[item_id] = meta
        ids.append(item_id)
        _audit("document.created", item_id, {"path": item.path, "size_bytes": size})
    _save_index(index)
    return {"doc_ids": ids}


@app.get("/api/v1/documents", dependencies=[Depends(verify_token)])
async def list_documents() -> dict[str, Any]:
    return {"documents": list(_load_index().values())}


@app.get("/api/v1/documents/{doc_id}/content", dependencies=[Depends(verify_token)])
async def get_content(doc_id: str) -> dict[str, Any]:
    meta = _read_meta(doc_id)
    content = (_doc_dir(doc_id) / meta["content_file"]).read_text(encoding="utf-8")
    return {"doc_id": doc_id, "path": meta["path"], "content": content, "metadata": meta}


@app.get("/api/v1/documents/{doc_id}/raw", dependencies=[Depends(verify_token)])
async def get_raw(doc_id: str) -> dict[str, Any]:
    return await get_content(doc_id)


@app.put("/api/v1/documents/{doc_id}", dependencies=[Depends(verify_token)])
async def update_document(doc_id: str, payload: UpdateDocumentRequest) -> dict[str, Any]:
    size = _content_size(payload.content)
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="file troppo grande")
    meta = _read_meta(doc_id)
    folder = _doc_dir(doc_id)
    (folder / meta["content_file"]).write_text(payload.content, encoding="utf-8")
    meta["updated_at"] = _now()
    meta["content_hash"] = _content_hash(payload.content)
    meta["size_bytes"] = size
    _write_json(folder / "meta.json", meta)
    index = _load_index()
    index[doc_id] = meta
    _save_index(index)
    _audit("document.updated", doc_id, {"author": payload.author, "message": payload.message})
    return {"status": "ok", "doc_id": doc_id, "path": meta["path"]}


@app.delete("/api/v1/documents/{doc_id}", dependencies=[Depends(verify_token)])
async def delete_document(doc_id: str) -> dict[str, Any]:
    folder = _doc_dir(doc_id)
    if not folder.exists():
        raise HTTPException(status_code=404, detail="document not found")
    for child in folder.iterdir():
        child.unlink()
    folder.rmdir()
    index = _load_index()
    index.pop(doc_id, None)
    _save_index(index)
    _audit("document.deleted", doc_id, {})
    return {"status": "ok", "doc_id": doc_id}


@app.get("/api/v1/sections", dependencies=[Depends(verify_token)])
async def list_sections() -> dict[str, Any]:
    sections = sorted({str(item.get("section", "")) for item in _load_index().values() if item.get("section")})
    return {"sections": sections}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("WIKI_SERVICE_PORT", "8200")))
