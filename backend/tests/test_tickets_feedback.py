import pytest
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_ticket_creation_and_auto_classification(client: AsyncClient) -> None:
    token = create_access_token("agent_tck", "tenant_tck_01", "agent", "tck@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Register customer via conversation
    conv_res = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"customer_name": "Diana Prince", "channel": "web"},
    )
    cust_id = conv_res.json()["data"]["customer_id"]

    # 2. Create ticket with billing issue
    ticket_res = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "customer_id": cust_id,
            "subject": "Overcharged on monthly subscription invoice",
            "description": "I noticed an unexpected $45 charge on my credit card invoice.",
        },
    )
    assert ticket_res.status_code == 200
    tck = ticket_res.json()["data"]
    assert tck["category"] == "billing"
    assert tck["priority"] in ["medium", "high", "urgent"]
    assert tck["status"] == "new"
    assert tck["ticket_number"].startswith("TCK-")
    assert tck["sla_due_at"] is not None
    assert len(tck["notes"]) >= 1
    assert tck["notes"][0]["note_type"] == "system_audit"


@pytest.mark.asyncio
async def test_duplicate_ticket_detection(client: AsyncClient) -> None:
    token = create_access_token("agent_tck", "tenant_tck_02", "agent", "tck2@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    conv_res = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"customer_name": "Bruce Wayne", "channel": "web"},
    )
    cust_id = conv_res.json()["data"]["customer_id"]

    # Ticket 1: Initial submission
    res1 = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "customer_id": cust_id,
            "subject": "Damaged package received during transit",
            "description": "The outer packaging was torn and the product inside was cracked.",
        },
    )
    assert res1.status_code == 200

    # Ticket 2: Duplicate submission within 24h with same subject -> 409 Conflict
    res2 = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "customer_id": cust_id,
            "subject": "Damaged package received during transit",
            "description": "Submitting again because I haven't heard back yet.",
        },
    )
    assert res2.status_code == 409
    assert "Duplicate ticket detected" in res2.json()["error"]["message"]


@pytest.mark.asyncio
async def test_8_stage_lifecycle_state_transitions(client: AsyncClient) -> None:
    token = create_access_token("agent_tck", "tenant_tck_03", "agent", "tck3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    conv_res = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"customer_name": "Barry Allen", "channel": "web"},
    )
    cust_id = conv_res.json()["data"]["customer_id"]

    # 1. Create ticket (status: new)
    create_res = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={
            "customer_id": cust_id,
            "subject": "Reschedule dental cleaning appointment",
            "description": "Need to move cleaning to next week due to business travel.",
        },
    )
    tck_id = create_res.json()["data"]["id"]
    assert create_res.json()["data"]["status"] == "new"

    # 2. Assign ticket (status: assigned)
    assign_res = await client.patch(
        f"/api/v1/tickets/{tck_id}/assign",
        headers=headers,
        json={"assigned_user_id": "agent_jessica_42"},
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["data"]["status"] == "assigned"
    assert assign_res.json()["data"]["assigned_user_id"] == "agent_jessica_42"

    # 3. Transition to in_progress
    prog_res = await client.patch(
        f"/api/v1/tickets/{tck_id}/status",
        headers=headers,
        json={"status": "in_progress", "reason": "Contacting clinic calendar coordinator"},
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["data"]["status"] == "in_progress"

    # 4. Transition to waiting_customer
    wait_res = await client.patch(
        f"/api/v1/tickets/{tck_id}/status",
        headers=headers,
        json={"status": "waiting_customer", "reason": "Sent 3 available time slots to patient"},
    )
    assert wait_res.status_code == 200
    assert wait_res.json()["data"]["status"] == "waiting_customer"

    # 5. Transition to resolved
    res_res = await client.patch(
        f"/api/v1/tickets/{tck_id}/status",
        headers=headers,
        json={"status": "resolved", "reason": "Patient confirmed Friday 10:00 AM slot"},
    )
    assert res_res.status_code == 200
    assert res_res.json()["data"]["status"] == "resolved"
    assert res_res.json()["data"]["resolved_at"] is not None

    # 6. Transition to closed
    close_res = await client.patch(
        f"/api/v1/tickets/{tck_id}/status",
        headers=headers,
        json={"status": "closed", "reason": "Resolution confirmed; closing ticket"},
    )
    assert close_res.status_code == 200
    assert close_res.json()["data"]["status"] == "closed"
    assert close_res.json()["data"]["closed_at"] is not None


@pytest.mark.asyncio
async def test_internal_notes_and_customer_replies(client: AsyncClient) -> None:
    token = create_access_token("agent_tck", "tenant_tck_04", "agent", "tck4@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    conv_res = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"customer_name": "Arthur Curry", "channel": "web"},
    )
    cust_id = conv_res.json()["data"]["customer_id"]

    tck_res = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={"customer_id": cust_id, "subject": "Shipping inquiry", "description": "Where is my parcel?"},
    )
    tck_id = tck_res.json()["data"]["id"]

    # 1. Add internal note (staff only)
    internal_res = await client.post(
        f"/api/v1/tickets/{tck_id}/notes",
        headers=headers,
        json={"content": "Checked DHL tracking; package held in customs warehouse.", "note_type": "internal"},
    )
    assert internal_res.status_code == 200
    assert internal_res.json()["data"]["note_type"] == "internal"

    # 2. Add customer reply
    reply_res = await client.post(
        f"/api/v1/tickets/{tck_id}/notes",
        headers=headers,
        json={"content": "Hello Arthur, customs has cleared your shipment today.", "note_type": "customer_reply"},
    )
    assert reply_res.status_code == 200
    assert reply_res.json()["data"]["note_type"] == "customer_reply"


@pytest.mark.asyncio
async def test_feedback_request_and_submission(client: AsyncClient) -> None:
    token = create_access_token("agent_tck", "tenant_tck_05", "agent", "tck5@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    conv_res = await client.post(
        "/api/v1/chat/conversations",
        headers=headers,
        json={"customer_name": "Victor Stone", "channel": "web"},
    )
    cust_id = conv_res.json()["data"]["customer_id"]

    tck_res = await client.post(
        "/api/v1/tickets",
        headers=headers,
        json={"customer_id": cust_id, "subject": "Account unlock", "description": "Reset password issue"},
    )
    tck_id = tck_res.json()["data"]["id"]

    # 1. Trigger feedback request (e.g. WhatsApp or Email)
    req_res = await client.post(
        f"/api/v1/tickets/{tck_id}/feedback-request",
        headers=headers,
        json={"channel": "whatsapp"},
    )
    assert req_res.status_code == 200
    fb_token = req_res.json()["data"]["token"]
    assert fb_token is not None

    # 2. Customer submits feedback via secure token
    submit_res = await client.post(
        "/api/v1/tickets/feedback/submit",
        json={
            "token": fb_token,
            "rating": 5,
            "was_resolved": True,
            "comment": "Support specialist was extraordinarily fast and helpful!",
        },
    )
    assert submit_res.status_code == 200
    fb_data = submit_res.json()["data"]
    assert fb_data["rating"] == 5
    assert fb_data["was_resolved"] is True
    assert fb_data["submitted_at"] is not None

    # 3. Duplicate submission attempt with same token -> 400 Bad Request
    dup_res = await client.post(
        "/api/v1/tickets/feedback/submit",
        json={"token": fb_token, "rating": 4, "was_resolved": True},
    )
    assert dup_res.status_code == 400
    assert "already been submitted" in dup_res.json()["error"]["message"]


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation_tickets(client: AsyncClient) -> None:
    token_a = create_access_token("user_a", "tenant_alpha_tck", "admin", "a@alpha.com")
    token_b = create_access_token("user_b", "tenant_beta_tck", "admin", "b@beta.com")

    # Tenant Alpha creates customer & ticket
    conv_a = await client.post(
        "/api/v1/chat/conversations",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"customer_name": "Clark Kent", "channel": "web"},
    )
    cust_a_id = conv_a.json()["data"]["customer_id"]

    tck_a = await client.post(
        "/api/v1/tickets",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"customer_id": cust_a_id, "subject": "Alpha Classified Issue", "description": "Confidential matter"},
    )
    tck_a_id = tck_a.json()["data"]["id"]

    # Tenant Beta lists tickets -> 0 returned
    list_b = await client.get("/api/v1/tickets", headers={"Authorization": f"Bearer {token_b}"})
    assert list_b.status_code == 200
    assert len(list_b.json()["data"]) == 0

    # Tenant Beta attempts to get Tenant Alpha's ticket -> 404 Not Found
    get_b = await client.get(f"/api/v1/tickets/{tck_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert get_b.status_code == 404

    # Tenant Beta attempts to update status of Tenant Alpha's ticket -> 404 Not Found
    patch_b = await client.patch(
        f"/api/v1/tickets/{tck_a_id}/status",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"status": "resolved"},
    )
    assert patch_b.status_code == 404
