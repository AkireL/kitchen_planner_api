import pytest


@pytest.mark.anyio
async def test_is_live(client):
    response = await client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"data": "API working fine"}
