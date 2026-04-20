import pytest


async def register_and_login(client, email="t@t.com"):
    await client.post("/auth/register", json={"email": email, "password": "pass", "full_name": "T"})
    res = await client.post("/auth/login", json={"email": email, "password": "pass"})
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_list_tickets_empty(client):
    token = await register_and_login(client)
    res = await client.get("/tickets", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_create_ticket(client):
    token = await register_and_login(client, "ticket@t.com")

    # Create a conversation first
    conv_res = await client.post("/chat/conversations", headers={"Authorization": f"Bearer {token}"})
    assert conv_res.status_code == 201
    conv_id = conv_res.json()["id"]

    res = await client.post("/tickets", json={
        "title": "My order is missing",
        "description": "Order #1234 has not arrived",
        "category": "order",
        "conversation_id": conv_id,
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "My order is missing"
    assert data["status"] == "open"
    assert data["priority"] == "medium"


@pytest.mark.asyncio
async def test_update_ticket_status(client):
    token = await register_and_login(client, "upd@t.com")
    conv_res = await client.post("/chat/conversations", headers={"Authorization": f"Bearer {token}"})
    conv_id = conv_res.json()["id"]

    ticket_res = await client.post("/tickets", json={
        "title": "Test ticket", "conversation_id": conv_id
    }, headers={"Authorization": f"Bearer {token}"})
    ticket_id = ticket_res.json()["id"]

    res = await client.patch(f"/tickets/{ticket_id}", json={"status": "resolved"},
                             headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "resolved"
