import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.first
class TestUsers:

    @pytest.mark.parametrize(
        'user_data',
        (
            {'login': 'admin', 'password': 'admin', 'is_staff': True},
        )
    )
    async def test_register_user(self, async_client: AsyncClient, user_data: dict):
        response = await async_client.post("/registration", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED, response.text
        response_data = response.json()
        assert response_data['login'] == user_data['login']

    @pytest.mark.parametrize(
        ('auth_data', 'expected'),
        (
            ({'username': 'admin', 'password': 'admin'}, True),
            ({'username': '123', 'password': '123'}, False),
        )
    )
    async def test_authenticate_user(self, async_client: AsyncClient, auth_data: dict, expected: bool):
        response = await async_client.post("/login", data=auth_data)
        assert expected == (response.status_code == status.HTTP_200_OK), response.text

        if not expected:
            return

        response_json = response.json()
        token = response_json['access_token']

        response = await async_client.get(f"/users/me", headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == status.HTTP_200_OK, response.text
        response_data = response.json()
        assert response_data['login'] == auth_data['username']


