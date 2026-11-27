# Business Capabilities Specification

BankingAIPlatform is engineered to support diverse business models without code bifurcation.

## Business Model Configuration Modes

1. **Products Mode:**
   - Catalog management (SKU, brand, category, pricing, stock, specs).
   - Order tracking, supplier relationships, inventory alerts.
   - Ideal for retail, e-commerce, and wholesale distributors.

2. **Services Mode:**
   - Service catalog (durations, pricing tiers, staff assignment).
   - Appointment booking, capacity management, scheduling, service delivery status.
   - Ideal for clinics, consultancies, agencies, salons, and maintenance firms.

3. **Products & Services (Hybrid) Mode:**
   - Unified catalog supporting physical inventory alongside appointment/service bookings.
   - Configurable per-tenant dynamically in organization settings.

## Business Data Hub (Integration Matrix)

- **Google Sheets:** Read-only OAuth connection with auto/manual sync and schema mapping.
- **Excel & CSV:** File upload parsing with preview, column mapping, and data validation.
- **Built-in Data Manager:** Native relational CRUD operations for businesses without external databases.
- **Database Connectors:** Read-only connections to tenant PostgreSQL or SQL databases.
