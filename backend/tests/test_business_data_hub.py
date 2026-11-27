import pytest
from httpx import AsyncClient
from app.core.security import create_access_token
from app.services.data_quality import DataQualityEngine
from app.services.connectors.google_sheets import GoogleSheetsConnector


@pytest.mark.asyncio
async def test_business_mode_configuration_toggle(client: AsyncClient) -> None:
    token = create_access_token(
        subject="admin_user",
        tenant_id="tenant_mode_test",
        role="admin",
        email="admin@modetest.com",
    )

    # 1. Read default mode
    res = await client.get("/api/v1/business/mode", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["data"]["business_mode"] == "hybrid"
    assert "inventory" in res.json()["data"]["active_capabilities"]
    assert "appointments" in res.json()["data"]["active_capabilities"]

    # 2. Update to "services" only
    res_update = await client.patch(
        "/api/v1/business/mode",
        headers={"Authorization": f"Bearer {token}"},
        json={"mode": "services"},
    )
    assert res_update.status_code == 200
    caps = res_update.json()["data"]["active_capabilities"]
    assert "appointments" in caps
    assert "inventory" not in caps


@pytest.mark.asyncio
async def test_product_crud_and_tenant_isolation(client: AsyncClient) -> None:
    token_a = create_access_token("admin_a", "tenant_company_a", "admin", "a@test.com")
    token_b = create_access_token("admin_b", "tenant_company_b", "admin", "b@test.com")

    # 1. Company A creates product
    res_create = await client.post(
        "/api/v1/business/products",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "sku": "ACME-SKU-990",
            "name": "Dental Floss Premium",
            "price": 14.50,
            "stock_quantity": 100,
            "category": "Oral Care",
        },
    )
    assert res_create.status_code == 200
    assert res_create.json()["data"]["sku"] == "ACME-SKU-990"

    # 2. Company A can list it
    res_list_a = await client.get("/api/v1/business/products", headers={"Authorization": f"Bearer {token_a}"})
    assert len(res_list_a.json()["data"]) == 1
    assert res_list_a.json()["data"][0]["sku"] == "ACME-SKU-990"

    # 3. Company B lists products -> Zero products (Isolated)
    res_list_b = await client.get("/api/v1/business/products", headers={"Authorization": f"Bearer {token_b}"})
    assert len(res_list_b.json()["data"]) == 0


@pytest.mark.asyncio
async def test_data_quality_engine_diagnostics() -> None:
    raw_products = [
        {"sku": "SKU-001", "name": "Toothpaste", "price": "5.99"},
        {"sku": "SKU-001", "name": "Duplicate SKU Item", "price": "10.00"},  # Duplicate SKU
        {"sku": "SKU-002", "name": "Negative Price Item", "price": "-15.00"},  # Negative Price
        {"sku": "", "name": "Missing SKU Item", "price": "8.00"},  # Missing SKU
    ]

    score, issues = DataQualityEngine.validate_products(raw_products)
    assert score < 100
    assert len(issues) >= 3

    issue_types = [i["issue_type"] for i in issues]
    assert "duplicate_record" in issue_types
    assert "invalid_price" in issue_types
    assert "missing_required_field" in issue_types


@pytest.mark.asyncio
async def test_csv_import_with_mapping(client: AsyncClient) -> None:
    token = create_access_token("admin_csv", "tenant_csv_01", "admin", "admin@csv.com")
    csv_text = """Item Code,Product Label,Selling Price,Inventory
CSV-01,Sonic Brush,49.99,30
CSV-02,Replacement Head,9.99,120"""

    response = await client.post(
        "/api/v1/business/import/csv",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "csv_content": csv_text,
            "column_mapping": {
                "Item Code": "sku",
                "Product Label": "name",
                "Selling Price": "price",
                "Inventory": "stock_quantity",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["records_processed"] == 2
    assert data["records_created"] == 2
    assert data["quality_score"] == 100
    assert len(data["issues_detected"]) == 0


def test_google_sheets_connector() -> None:
    test_result = GoogleSheetsConnector.test_connection({"spreadsheet_id": "sheet_12345", "title": "Test Sheet"})
    assert test_result["connected"] is True
    assert test_result["mode"] == "read_only"
    assert "Stock" in test_result["worksheets"]

    records = GoogleSheetsConnector.fetch_worksheet_records("sheet_12345", "Stock")
    assert len(records) == 3
    assert records[0]["SKU"] == "ACME-PROD-01"
