from pathlib import Path
from datetime import datetime
from src.params.config import config
from fastapi import UploadFile
from requests import Session
from starlette import status
from starlette.exceptions import HTTPException
from logs import get_logger
from src.schemas.media_schemas import UploadResult, StorageItem

logger = get_logger(__name__)


class YandexDiscAPI:
    session: Session
    work_dir: str
    root_path: Path = Path('backend:/')

    def __init__(self, token: str, work_dir: str):
        self.auth_headers = {
            'Authorization': f'OAuth {token}'
        }
        self.work_dir = work_dir
        self.session = Session()

    @property
    def root(self) -> Path:
        return self.root_path / self.work_dir

    def _build_filename(self, filename: str) -> str:
        ind = filename.find('.')
        file_name = filename[:ind] + '_' + datetime.now(tz=config.time_zone_ino).strftime('%Y-%m-%d_%H:%M:%S') + filename[ind:]
        return file_name

    async def _upload_file(self, file: UploadFile, path: str = '', overwrite: bool = True, keep_name: bool = False) -> Path:
        content = await file.read()
        filename = file.filename if keep_name else self._build_filename(file.filename)
        upload_file_path = str(self.root / path / filename)

        path_query_params = {
            'overwrite': overwrite,
            'path': upload_file_path,
        }

        # Получаем ссылку, по которой нужно загружать файл
        path_response = self.session.get('https://cloud-api.yandex.net/v1/disk/resources/upload', params=path_query_params, headers=self.auth_headers)

        if not path_response.ok:
            logger.error(f'Cant upload url for file "{upload_file_path}": {path_response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалось получить доступ к загрузке файла "{upload_file_path}": {path_response.json().get("message", "unknown")}')

        # Загружаем целевой файл по полученной сылке
        upload_path = path_response.json()['href']
        upload_response = self.session.put(upload_path, data=content, headers=self.auth_headers)

        if upload_response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            logger.error(f'File "{filename}" is too large ({file.size})')
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, f'Файл "{filename}" слишком большой')

        if not upload_response.ok:
            logger.error(f'Cant upload file "{upload_file_path}": {upload_response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалось загрузить файл: {upload_response.json().get("message", "unknown")}')

        return upload_file_path

    def _publish_file(self, file_path: Path | str) -> str | None:
        params = {
            'path': str(file_path)
        }
        response = self.session.put('https://cloud-api.yandex.net/v1/disk/resources/publish', params=params, headers=self.auth_headers)

        if not response.ok:
            logger.error(f'Cant publish file "{file_path}": {response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалось опубликовать файл "{file_path}": {response.json().get("message", "unknown")}')

        json_data = response.json()

        metadata_path = json_data.get('href', None)
        if not metadata_path:
            raise HTTPException

        meta_info_response = self.session.get(metadata_path, headers=self.auth_headers)

        if not response.ok:
            logger.error(f'Cant read metainfo of file "{file_path}": {meta_info_response.text} \nLink: {metadata_path}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалось получить публичную ссылку на файл "{file_path}": {meta_info_response.json().get("message", "unknown")}')

        meta_data = meta_info_response.json()

        return meta_data.get('public_url', None)

    def delete_source(self, path: Path, permanently: bool = False) -> None:
        params = {
            'path': str(self.root / path),
            'permanently': permanently
        }
        response = self.session.delete('https://cloud-api.yandex.net/v1/disk/resources', params=params, headers=self.auth_headers)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            logger.error(f'File not found: {str(path)}')
            raise HTTPException(status.HTTP_404_NOT_FOUND, f'Файл не найден: {str(path)}')

        elif not response.ok:
            logger.error(f'Error deleting file "{str(path)}": {response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Ошибка при удалении файла "{str(path)}": {response.json().get("message", "unknown")}')

    async def upload_file(self, file: UploadFile, path: str = '', overwrite: bool = True, publish: bool = True, keep_name: bool = False) -> UploadResult:
        result = {
            'overwrite_mode': overwrite,
        }

        file_path = await self._upload_file(file, path, overwrite, keep_name=keep_name)
        result['storage_path'] = str(file_path)

        if publish:
            public_url = self._publish_file(file_path)
            result['href'] = public_url

        return UploadResult(**result)

    def get_files(self, path: str | Path = '') -> list[StorageItem]:
        limit = 1000
        offset = 0

        result = []

        while True:
            params = {
                'path': str(self.root / path),
                'offset': offset,
                'limit': limit
            }
            response = self.session.get('https://cloud-api.yandex.net/v1/disk/resources', params=params, headers=self.auth_headers)

            if not response.ok:
                logger.error(f'Cant get files from "{str(self.root / path)}": {response.text}')
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалось получить файлы каталога "{str(self.root / path)}": {response.json().get("message", "unknown")}')

            json_data = response.json()

            for item in json_data.get('_embedded', {}).get('items', []):
                result.append(
                    StorageItem(
                        name=item.get('name', None),
                        path=item.get('path', None),
                        item_type=item.get('type', None),
                        file=item.get('file', None),
                        public_key=item.get('public_key', None),
                        public_url=item.get('public_url', None),
                        size=item.get('size', None),
                        created_at=item.get('created', None),
                    )
                )

            if json_data.get('_embedded', {}).get('total', 0) < limit:
                return result

            offset += limit

    def create_directory(self, path: str) -> None:
        new_dir_path = str(self.root / path)
        params = {
            'path': new_dir_path
        }
        response = self.session.put('https://cloud-api.yandex.net/v1/disk/resources', headers=self.auth_headers, params=params)

        if not response.ok:
            logger.error(f'Cant create directory "{new_dir_path}": {response.text}')
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Не удалось создать папку "{new_dir_path}": {response.json().get("message", "unknown")}')







