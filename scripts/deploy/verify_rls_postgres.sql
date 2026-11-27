-- ============================================================================
-- BankingAIPlatform Native PostgreSQL 16 + pgvector Row-Level Security (RLS)
-- Stage D & Stage F Database Verification Script
-- Execute against staging PostgreSQL 16 instance after `alembic upgrade head`
-- ============================================================================

-- 1. Verify pgvector extension is active
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- 2. Enable Row-Level Security on core tenant-scoped tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 3. Create strict tenant isolation policies bound to app.current_tenant_id
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY['customers', 'conversations', 'messages', 'tickets', 'documents', 'audit_logs']
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY tenant_isolation_policy ON %I USING (tenant_id = current_setting(''app.current_tenant_id'', true));',
            tbl
        );
    END LOOP;
END $$;

-- 4. Independent Cross-Tenant Isolation Verification Test (Read-Only Transaction)
BEGIN;
    -- Simulate Tenant A context
    SET LOCAL app.current_tenant_id = 'tenant_rls_verify_alpha';
    SELECT count(*) AS tenant_alpha_visible_customers FROM customers;

    -- Switch to Tenant B context
    SET LOCAL app.current_tenant_id = 'tenant_rls_verify_beta';
    SELECT count(*) AS tenant_beta_visible_customers FROM customers;
ROLLBACK;
