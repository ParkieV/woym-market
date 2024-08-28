from pathlib import Path

from requests import Session
from starlette import status
from starlette.exceptions import HTTPException


class YandexDiscAPI:
    session: Session
    work_dir: str
    root_path: Path = Path('app:/')

    def __init__(self, work_dir: str):
        self.work_dir = work_dir
        self.session = Session()

    @property
    def root(self) -> Path:
        return self.root_path / self.work_dir

    def _upload_file(self, file, path: str = '.', overwrite: bool = False) -> Path:
        path_query_params = {
            'overwrite': overwrite,
            'path': str(self.root / path / file.filename),
        }
        path_response = self.session.get('https://cloud-api.yandex.net/v1/disk/resources/upload', params=path_query_params)

        if path_response.status_code != 200:
            raise HTTPException

        upload_path = path_response.json()['href']

        upload_response = self.session.put(upload_path, data=file)

        if not upload_response.ok:
            raise HTTPException

        return self.root / path / file.filename

    def _publish_file(self, file_path: Path | str) -> str | None:
        params = {
            'path': str(file_path)
        }
        response = self.session.put('https://cloud-api.yandex.net/v1/disk/resources/publish', params=params)

        if response.status_code != status.HTTP_200_OK:
            raise HTTPException

        json_data = response.json()

        metadata_path = json_data.get('href', None)
        if not metadata_path:
            raise HTTPException

        meta_info_response = self.session.get(metadata_path)

        if not response.ok:
            raise HTTPException


        meta_data = meta_info_response.json()

        return meta_data.get('public_url', None)



    def delete_file(self, file_path: Path) -> None:
        params = {
            'path': str(file_path),
        }
        response = self.session.delete('https://cloud-api.yandex.net/v1/disk/resources', params=params)
        if not response.ok:
            raise HTTPException

    def upload_file(self, file: bytes, path: str, overwrite: bool = False) -> str:
        file_path = self._upload_file(file, path, overwrite)


        public_url = self._publish_file(file_path)

        return public_url


    def files_all(self):




