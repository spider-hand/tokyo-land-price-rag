from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from drf_spectacular.generators import SchemaGenerator

from rag import messages
from rag.qdrant import build_filter


@pytest.fixture
def dependencies(monkeypatch):
    mocks = SimpleNamespace(
        openai=Mock(),
        qdrant=Mock(),
        intent=Mock(return_value={"ward": "渋谷"}),
        embed=Mock(return_value=[0.1]),
        retrieve=Mock(return_value=SimpleNamespace(hits=[object()], contexts=["data"])),
        generate=Mock(return_value="answer"),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("QDRANT_URL", "http://qdrant:6333")
    monkeypatch.setattr(messages, "OpenAI", mocks.openai)
    monkeypatch.setattr(messages, "QdrantClient", mocks.qdrant)
    monkeypatch.setattr(messages, "extract_intent", mocks.intent)
    monkeypatch.setattr(messages, "embed", mocks.embed)
    monkeypatch.setattr(messages, "retrieve_contexts", mocks.retrieve)
    monkeypatch.setattr(messages, "generate_with_llm", mocks.generate)
    return mocks


def test_message_with_intent(client, dependencies):
    response = client.post(
        "/api/v1/messages/", {"message": "渋谷"}, content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json() == {"response": "answer", "ward": "渋谷"}
    dependencies.openai.assert_called_once_with(api_key="test-key")
    dependencies.qdrant.assert_called_once_with(url="http://qdrant:6333")
    query_filter = dependencies.retrieve.call_args.args[2]
    assert query_filter.must[0].key == "ward"
    assert query_filter.must[0].match.value == "渋谷"
    dependencies.generate.assert_called_once_with(
        dependencies.openai.return_value, question="渋谷", contexts=["data"]
    )


@pytest.mark.parametrize(("is_point", "size"), [(True, 100), (False, 500)])
def test_message_with_coordinates(client, dependencies, is_point, size):
    response = client.post(
        "/api/v1/messages/",
        {"message": "nearby", "lat": 35.0, "lon": 139.0, "is_point": is_point},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json() == {"response": "answer", "ward": None}
    dependencies.intent.assert_not_called()
    box = dependencies.retrieve.call_args.args[2].must[0].geo_bounding_box
    assert box.top_left.lat == pytest.approx(35 + size / 2 / 111000)
    assert box.bottom_right.lon == pytest.approx(139 + size / 2 / 91000)


def test_partial_coordinates_use_intent(client, dependencies):
    response = client.post(
        "/api/v1/messages/",
        {"message": "question", "lat": 35},
        content_type="application/json",
    )
    assert response.status_code == 200
    dependencies.intent.assert_called_once()


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("ja", "関連する情報が見つかりませんでした。"),
        ("en", "No relevant information was found."),
    ],
)
def test_no_results(client, dependencies, language, expected):
    dependencies.retrieve.return_value = SimpleNamespace(hits=[], contexts=[])
    response = client.post(
        "/api/v1/messages/",
        {"message": "question", "language": language},
        content_type="application/json",
    )
    assert response.json() == {"response": expected, "ward": None}
    dependencies.generate.assert_not_called()


@pytest.mark.parametrize("body", [{}, {"message": "test", "lat": "invalid"}])
def test_invalid_request(client, body):
    response = client.post("/api/v1/messages/", body, content_type="application/json")
    assert response.status_code == 400


def test_get_not_allowed(client):
    assert client.get("/api/v1/messages/").status_code == 405


def test_filter_conditions():
    query = build_filter(
        {"station": "新宿", "time_to_station_max": 10, "require_max_price": True}
    )
    assert [condition.key for condition in query.must] == [
        "station",
        "time_to_station",
        "is_max_price",
    ]
    assert query.must[1].range.lte == 10
    assert build_filter({}) is None


def test_messages_schema():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    operation = schema["paths"]["/api/v1/messages/"]["post"]
    assert operation["requestBody"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/MessageRequest")
    assert operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/MessageResponse")
