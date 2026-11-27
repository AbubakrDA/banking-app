from app.models.base import TenantScopedModel
from app.models.tenant import Tenant, OrganizationSettings
from app.models.user import User
from app.models.customer import Customer
from app.models.conversation import Conversation, Message


def test_tenant_scoped_models_have_tenant_id() -> None:
    tenant_models = [
        OrganizationSettings,
        User,
        Customer,
        Conversation,
        Message,
    ]
    for model in tenant_models:
        assert issubclass(model, TenantScopedModel), f"{model.__name__} must inherit TenantScopedModel"
        assert hasattr(model, "tenant_id"), f"{model.__name__} must contain tenant_id column"


def test_tenant_model_defaults() -> None:
    tenant = Tenant(name="Test Tenant", slug="test-tenant")
    assert tenant.business_mode == "hybrid"
    assert tenant.name == "Test Tenant"


def test_customer_model_fields() -> None:
    customer = Customer(tenant_id="tenant_01", name="Sarah Jenkins", email="sarah@example.com")
    assert customer.tenant_id == "tenant_01"
    assert customer.tier == "standard"


def test_conversation_model_fields() -> None:
    conv = Conversation(tenant_id="tenant_01", customer_id="cust_01", channel="web")
    assert conv.status == "active"
    assert conv.channel == "web"
