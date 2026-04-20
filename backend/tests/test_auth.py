import pytest


@pytest.mark.asyncio
async def test_register(client):
    res = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "pass", "full_name": "Dup"}
    await client.post("/auth/register", json=payload)
    res = await client.post("/auth/register", json=payload)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "login@example.com", "password": "secret", "full_name": "Login User"
    })
    res = await client.post("/auth/login", json={"email": "login@example.com", "password": "secret"})
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "wp@example.com", "password": "correct", "full_name": "WP User"
    })
    res = await client.post("/auth/login", json={"email": "wp@example.com", "password": "wrong"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
