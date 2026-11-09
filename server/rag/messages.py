import os

from openai import OpenAI
from qdrant_client import QdrantClient

from .openai import embed, extract_intent, generate_with_llm
from .qdrant import build_filter, build_geo_filter, retrieve_contexts


def post_message(data: dict) -> dict:
    openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    qdrant = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
    message = data["message"]
    lat, lon = data.get("lat"), data.get("lon")
    ward = None

    if lat is not None and lon is not None:
        query_filter = build_geo_filter(lat, lon, 100 if data.get("is_point") else 500)
    else:
        intent = extract_intent(openai, message)
        query_filter = build_filter(intent)
        ward = intent.get("ward")

    vector = embed(openai, message)
    result = retrieve_contexts(qdrant, vector, query_filter)
    if not result.hits:
        response = (
            "関連する情報が見つかりませんでした。"
            if data.get("language", "en") == "ja"
            else "No relevant information was found."
        )
        return {"response": response, "ward": None}

    response = generate_with_llm(openai, question=message, contexts=result.contexts)
    return {"response": response, "ward": ward}
