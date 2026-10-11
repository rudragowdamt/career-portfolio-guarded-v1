from fastapi.testclient import TestClient
from main import app
@app.middleware("http")
async def inject_gateway_identity(request, call_next):
    request.scope["aws.event"] = {
        "requestContext": {"identity": {"sourceIp": "192.0.2.10"}}
    }
    return await call_next(request)

client=TestClient(app)
def test_health():
    assert client.get("/health").json()["status"]=="ok"
def test_sources():
    assert len(client.get("/sources").json())>=5
def test_chat():
    r=client.post("/chat",json={"question":"What AWS projects were built?"})
    assert r.status_code==200
    assert r.json()["sources"]
def test_bad_question():
    assert client.post("/chat",json={"question":"x"}).status_code==422
def test_no_evidence():
    r=client.post("/chat",json={"question":"quantum banana spaceship?"})
    assert r.status_code==200
    assert not r.json()["sources"]
