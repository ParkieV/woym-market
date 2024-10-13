import pytest
from src.params.confing import config
from src.api.yandex.disk import YandexDiscAPI


class TestYandexDiskAPI:
    @pytest.fixture(scope='class')
    def _api(self) -> YandexDiscAPI:
        return YandexDiscAPI('', 'dev')

    @pytest.mark.parametrize(
        'token,work_dir,is_valid',
        [
            ('jkjbk45hv35h35ihl34h5v3h', False),
            ('', False),
            (config.yandex_disk_token, True)
        ]
    )
    def test_init_api(self, token: str, work_dir: str, is_valid: bool):
        pass