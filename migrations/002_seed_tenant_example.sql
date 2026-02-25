-- Example: insert a tenant with an API key (run after 001_initial.sql).
-- Replace with your values. Keep api_key secret for production.
/*
INSERT INTO tenants (id, name, contact_email, api_key)
VALUES (
  gen_random_uuid(),
  'Demo Tenant',
  'benefits@example.com',
  'your-api-key-here'
);
*/
