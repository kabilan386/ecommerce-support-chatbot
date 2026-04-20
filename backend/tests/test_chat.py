import pytest


async def get_token(client, email="c@c.com"):
    await client.post("/auth/register", json={"email": email, "password": "pass", "full_name": "C"})
    res = await client.post("/auth/login", json={"email": email, "password": "pass"})
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_create_conversation(client):
    token = await get_token(client)
    res = await client.post("/chat/conversations", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_list_conversations(client):
    token = await get_token(client, "list@c.com")
    await client.post("/chat/conversations", headers={"Authorization": f"Bearer {token}"})
    await client.post("/chat/conversations", headers={"Authorization": f"Bearer {token}"})
    res = await client.get("/chat/conversations", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 2


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    res = await client.get("/chat/conversations")
    assert res.status_code == 403
