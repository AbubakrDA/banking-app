import pytest
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_semantic_question_clustering(client: AsyncClient) -> None:
    token = create_access_token("agent_nlp", "tenant_nlp_01", "agent", "nlp@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Log Question 1
    res1 = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={"raw_text": "What is your refund policy terms and refund guidelines?"},
    )
    assert res1.status_code == 200
    q1 = res1.json()["data"]
    cluster_id = q1["cluster_id"]
    assert cluster_id is not None
    assert q1["detected_intent"] == "return_policy"

    # 2. Log Question 2 (semantically similar)
    res2 = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={"raw_text": "What are your refund policy terms and return guidelines?"},
    )
    assert res2.status_code == 200
    q2 = res2.json()["data"]

    # Verify clustered into same QuestionCluster
    assert q2["cluster_id"] == cluster_id

    # 3. Check cluster frequency
    clusters_res = await client.get("/api/v1/nlp/clusters", headers=headers)
    assert clusters_res.status_code == 200
    clusters = clusters_res.json()["data"]
    matched_c = next(c for c in clusters if c["id"] == cluster_id)
    assert matched_c["frequency"] >= 2


@pytest.mark.asyncio
async def test_intent_and_language_detection(client: AsyncClient) -> None:
    token = create_access_token("agent_nlp", "tenant_nlp_02", "agent", "nlp2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Spanish Pricing Inquiry
    res_es = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={"raw_text": "Hola, cuánto cuesta el servicio por favor?"},
    )
    assert res_es.status_code == 200
    assert res_es.json()["data"]["detected_language"] == "es"
    assert res_es.json()["data"]["detected_intent"] == "pricing_inquiry"

    # 2. German Inquiry
    res_de = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={"raw_text": "Hallo danke, wie viel kostet das Produkt?"},
    )
    assert res_de.status_code == 200
    assert res_de.json()["data"]["detected_language"] == "de"

    # 3. English Shipping Timeline
    res_en = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={"raw_text": "When will my tracking delivery package arrive?"},
    )
    assert res_en.status_code == 200
    assert res_en.json()["data"]["detected_language"] == "en"
    assert res_en.json()["data"]["detected_intent"] == "shipping_timeline"


@pytest.mark.asyncio
async def test_knowledge_gap_detection(client: AsyncClient) -> None:
    token = create_access_token("agent_nlp", "tenant_nlp_03", "agent", "nlp3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log question with low RAG confidence (unanswered by KB)
    res = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={
            "raw_text": "Do you provide custom international shipping to Antarctica?",
            "rag_confidence_score": 0.35,  # Low confidence
        },
    )
    assert res.status_code == 200
    assert res.json()["data"]["was_rag_matched"] is False

    # Check Knowledge Gaps endpoint
    gap_res = await client.get("/api/v1/nlp/knowledge-gaps", headers=headers)
    assert gap_res.status_code == 200
    gaps = gap_res.json()["data"]
    assert len(gaps) >= 1
    target_gap = gaps[0]
    assert "Antarctica" in target_gap["canonical_question"]
    assert target_gap["suggested_faq_answer"] is not None


@pytest.mark.asyncio
async def test_trend_analytics_and_surging_detection(client: AsyncClient) -> None:
    token = create_access_token("agent_nlp", "tenant_nlp_04", "agent", "nlp4@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Simulate 5 questions on same topic to trigger "surging" status
    for i in range(5):
        await client.post(
            "/api/v1/nlp/questions",
            headers=headers,
            json={"raw_text": "Is there an outage with the payment gateway service?"},
        )

    # Call trends endpoint
    trends_res = await client.get("/api/v1/nlp/trends", headers=headers)
    assert trends_res.status_code == 200
    data = trends_res.json()["data"]

    assert data["total_questions"] >= 5
    assert len(data["surging_clusters"]) >= 1
    assert data["surging_clusters"][0]["trend_direction"] == "surging"
    assert "payment gateway" in data["surging_clusters"][0]["canonical_question"]
    assert len(data["intent_distribution"]) > 0


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_nlp(client: AsyncClient) -> None:
    token_a = create_access_token("user_a", "tenant_alpha_nlp", "admin", "a@alpha.com")
    token_b = create_access_token("user_b", "tenant_beta_nlp", "admin", "b@beta.com")

    # Tenant Alpha logs question
    await client.post(
        "/api/v1/nlp/questions",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"raw_text": "Alpha classified inquiry regarding quantum reactor keys"},
    )

    # Tenant Beta lists clusters -> 0 returned
    clusters_b = await client.get("/api/v1/nlp/clusters", headers={"Authorization": f"Bearer {token_b}"})
    assert clusters_b.status_code == 200
    assert len(clusters_b.json()["data"]) == 0

    # Tenant Beta queries trends -> 0 total questions
    trends_b = await client.get("/api/v1/nlp/trends", headers={"Authorization": f"Bearer {token_b}"})
    assert trends_b.status_code == 200
    assert trends_b.json()["data"]["total_questions"] == 0
    assert trends_b.json()["data"]["total_clusters"] == 0
