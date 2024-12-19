import pytest
from httpx import AsyncClient
from starlette import status

from tests.endpoints.offers.conftest import pricing_schemes


class TestOffersEndpoints:

    async def test_get_offers(self, async_client: AsyncClient, auth_token: str):
        response = await async_client.get('data/offers', headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == status.HTTP_200_OK, response.text

    @pytest.mark.parametrize(
        ('pricing_scheme_data', 'expected'),
        pricing_schemes()
    )
    async def test_create_pricing_schemes(self, async_client: AsyncClient, auth_token: str, pricing_scheme_data: dict,
                                          expected: bool):
        response = await async_client.post('data/pricing-schemes', json=pricing_scheme_data,
                                           headers={'Authorization': f'Bearer {auth_token}'})
        assert expected == (response.status_code == status.HTTP_200_OK), response.text
        assert expected == (response.json() == {'status': 'OK'})

    async def test_get_pricing_schemes(self, async_client: AsyncClient, auth_token: str):
        response = await async_client.get('data/pricing-schemes', headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == status.HTTP_200_OK, response.text
        assert len(response.json())

    # async def test_update_pricing_schemes(self, async_client: AsyncClient, auth_token: str, update_data: dict, expected: bool):
    #     response = await async_client.patch('data/pricing-schemes', headers={'Authorization': f'Bearer {auth_token}'}, json=)
    #     assert expected == (response.status_code == status.HTTP_200_OK, response.text)
