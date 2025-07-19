import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sannetic_explorer.api import app

@pytest.mark.asyncio
async def test_get_bodies_returns_star():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/celestial-bodies")
        assert response.status_code == 200
        bodies = response.json()
        # At least one body with type 'star'
        assert any(b.get('type') == 'star' for b in bodies)

@pytest.mark.asyncio
async def test_put_bodies_id_changes_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Get a body
        response = await ac.get("/celestial-bodies")
        assert response.status_code == 200
        bodies = response.json()
        body = bodies[0]
        body_id = body['id']
        # Change the name
        new_name = body['name'] + "_updated"
        put_resp = await ac.put(f"/bodies/{body_id}", json={"name": new_name})
        assert put_resp.status_code == 200
        # Fetch again and check
        get_resp = await ac.get(f"/celestial-bodies/{body_id}")
        assert get_resp.status_code == 200
        updated = get_resp.json()
        assert updated['name'] == new_name 