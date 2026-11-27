import pytest
import uuid
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_kpi_dashboard_aggregation(client: AsyncClient) -> None:
    token = create_access_token("admin_intel_01", "tenant_intel_01", "admin", "admin1@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create conversation (which registers customer)
    conv_res = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"customer_name": "Alice Corp", "channel": "web_chat"},
    )
    assert conv_res.status_code == 200
    cust_id = conv_res.json()["data"]["customer_id"]

    # 2. Create a ticket
    t_res = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "customer_id": cust_id,
            "subject": "System downtime inquiry",
            "description": "Production API responding with 500 error",
        },
    )
    assert t_res.status_code == 200

    # 4. Log a question via NLP
    q_res = await client.post(
        "/api/v1/nlp/questions",
        headers=headers,
        json={"raw_text": "What is the uptime SLA guarantee for enterprise plans?"},
    )
    assert q_res.status_code == 200

    # 5. Fetch KPIs
    kpi_res = await client.get("/api/v1/analytics/kpis", headers=headers)
    assert kpi_res.status_code == 200
    kpis = kpi_res.json()["data"]

    assert kpis["total_conversations"] >= 1
    assert kpis["ai_deflection_rate"] >= 0.0
    assert kpis["active_customers"] >= 1
    assert kpis["total_tickets"] >= 1
    assert kpis["urgent_tickets"] >= 1
    assert kpis["total_questions_logged"] >= 1
    assert "positive" in kpis["sentiment_breakdown"]


@pytest.mark.asyncio
async def test_ai_insights_generation_and_evidence_tiering(client: AsyncClient) -> None:
    token = create_access_token("admin_intel_02", "tenant_intel_02", "admin", "admin2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Generate insights
    gen_res = await client.post("/api/v1/analytics/insights/generate", headers=headers)
    assert gen_res.status_code == 200
    insights = gen_res.json()["data"]
    assert len(insights) >= 1

    first_insight = insights[0]
    insight_id = first_insight["id"]
    assert first_insight["evidence_tier"] in ["PROVEN", "PROBABLE", "PLAUSIBLE", "SPECULATIVE"]
    assert first_insight["confidence_score"] > 0.0
    assert first_insight["actionable_recommendation"] != ""
    assert first_insight["is_acknowledged"] is False

    # List insights
    list_res = await client.get("/api/v1/analytics/insights", headers=headers)
    assert list_res.status_code == 200
    assert any(i["id"] == insight_id for i in list_res.json()["data"])

    # Acknowledge insight
    ack_res = await client.patch(
        f"/api/v1/analytics/insights/{insight_id}/acknowledge",
        headers=headers,
        json={"acknowledged": True},
    )
    assert ack_res.status_code == 200
    ack_data = ack_res.json()["data"]
    assert ack_data["is_acknowledged"] is True
    assert ack_data["acknowledged_by"] == "admin_intel_02"


@pytest.mark.asyncio
async def test_organizational_memory_management(client: AsyncClient) -> None:
    token = create_access_token("admin_intel_03", "tenant_intel_03", "admin", "admin3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create organizational memory playbook
    entry_payload = {
        "category": "support",
        "title": "Holiday Shipping Delay Mitigation Playbook",
        "summary": "Standard operating guidelines for resolving delivery delays during peak holiday season.",
        "key_findings": [
            "Carrier capacity bottlenecks occur between Nov 20 and Dec 26.",
            "Customers respond positively to proactive tracking notification SMS.",
        ],
        "playbook_steps": [
            "1. Activate courier contingency partner.",
            "2. Send bulk status alert to affected order IDs.",
            "3. Offer 15% discount voucher on next purchase.",
        ],
        "tags": ["logistics", "shipping", "holidays"],
        "status": "active",
    }
    create_res = await client.post(
        "/api/v1/analytics/organizational-memory",
        headers=headers,
        json=entry_payload,
    )
    assert create_res.status_code == 200
    entry = create_res.json()["data"]
    assert entry["id"] is not None
    assert entry["category"] == "support"
    assert len(entry["playbook_steps"]) == 3

    # Query organizational memory
    list_res = await client.get(
        "/api/v1/analytics/organizational-memory?category=support",
        headers=headers,
    )
    assert list_res.status_code == 200
    memories = list_res.json()["data"]
    assert len(memories) >= 1
    assert memories[0]["title"] == "Holiday Shipping Delay Mitigation Playbook"


@pytest.mark.asyncio
async def test_governed_analytics_copilot_queries(client: AsyncClient) -> None:
    token = create_access_token("admin_intel_04", "tenant_intel_04", "admin", "admin4@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Query 1: Automation Deflection
    q1_res = await client.post(
        "/api/v1/analytics/copilot/query",
        headers=headers,
        json={"query": "What is our current AI deflection and automation rate?"},
    )
    assert q1_res.status_code == 200
    data1 = q1_res.json()["data"]
    assert data1["intent_detected"] == "automation_deflection_inquiry"
    assert "ai_deflection_rate" in data1["metrics"]
    assert data1["evidence_level"] == "PROVEN"
    assert len(data1["citations"]) >= 1

    # Query 2: Tickets & Complaints
    q2_res = await client.post(
        "/api/v1/analytics/copilot/query",
        headers=headers,
        json={"query": "How many open tickets and urgent complaints do we have?"},
    )
    assert q2_res.status_code == 200
    data2 = q2_res.json()["data"]
    assert data2["intent_detected"] == "ticket_operations_inquiry"
    assert "open_tickets" in data2["metrics"]

    # Query 3: Knowledge Gaps
    q3_res = await client.post(
        "/api/v1/analytics/copilot/query",
        headers=headers,
        json={"query": "Are there any knowledge gaps or unanswered FAQ topics?"},
    )
    assert q3_res.status_code == 200
    data3 = q3_res.json()["data"]
    assert data3["intent_detected"] == "knowledge_gap_inquiry"
    assert "knowledge_gaps_count" in data3["metrics"]


@pytest.mark.asyncio
async def test_executive_report_generation_and_export(client: AsyncClient) -> None:
    token = create_access_token("admin_intel_05", "tenant_intel_05", "admin", "admin5@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Generate Weekly Executive Report
    rep_res = await client.post(
        "/api/v1/analytics/reports/generate",
        headers=headers,
        json={"period_type": "weekly", "title": "Weekly Operations & Quality Briefing"},
    )
    assert rep_res.status_code == 200
    report = rep_res.json()["data"]
    report_id = report["id"]
    assert report["period_type"] == "weekly"
    assert report["title"] == "Weekly Operations & Quality Briefing"
    assert "kpis" in report

    # Export as JSON
    json_export = await client.get(
        f"/api/v1/analytics/reports/{report_id}/export?format=json",
        headers=headers,
    )
    assert json_export.status_code == 200
    json_data = json_export.json()["data"]
    assert json_data["format"] == "json"
    assert "banking_ai_report_" in json_data["filename"]
    assert "Weekly Operations & Quality Briefing" in json_data["content"]

    # Export as CSV
    csv_export = await client.get(
        f"/api/v1/analytics/reports/{report_id}/export?format=csv",
        headers=headers,
    )
    assert csv_export.status_code == 200
    csv_data = csv_export.json()["data"]
    assert csv_data["format"] == "csv"
    assert ".csv" in csv_data["filename"]
    assert "Metric,Value" in csv_data["content"]


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_analytics(client: AsyncClient) -> None:
    # Setup Tenant Alpha
    token_a = create_access_token("admin_a", "tenant_analytics_alpha", "admin", "alpha@test.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup Tenant Beta
    token_b = create_access_token("admin_b", "tenant_analytics_beta", "admin", "beta@test.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant Alpha creates an organizational memory entry
    await client.post(
        "/api/v1/analytics/organizational-memory",
        headers=headers_a,
        json={
            "category": "product",
            "title": "Alpha Confidential Product Roadmap Playbook",
            "summary": "Internal proprietary launch details for Alpha.",
            "status": "active",
        },
    )

    # Tenant Alpha generates an executive report
    await client.post(
        "/api/v1/analytics/reports/generate",
        headers=headers_a,
        json={"period_type": "monthly", "title": "Alpha Monthly Executive Audit"},
    )

    # Tenant Beta queries memory -> Must NOT see Alpha's playbook
    beta_mem_res = await client.get("/api/v1/analytics/organizational-memory", headers=headers_b)
    assert beta_mem_res.status_code == 200
    beta_memories = beta_mem_res.json()["data"]
    assert not any("Alpha Confidential" in m["title"] for m in beta_memories)

    # Tenant Beta queries reports -> Must NOT see Alpha's report
    beta_rep_res = await client.get("/api/v1/analytics/reports", headers=headers_b)
    assert beta_rep_res.status_code == 200
    beta_reports = beta_rep_res.json()["data"]
    assert not any("Alpha Monthly" in r["title"] for r in beta_reports)
