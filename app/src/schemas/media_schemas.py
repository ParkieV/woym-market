from pydantic import BaseModel


class UploadResult(BaseModel):
    storage_path: str
    filename: str | None
    href: str | None = None
    overwrite_mode: bool


class StorageItem(BaseModel):
    name: str | None = None
    path: str | None = None
    item_type: str | None = None
    file: str | None = None
    public_key: str | None = None
    public_url: str | None = None
    size: int | None = None
    created_at: str | None = None

