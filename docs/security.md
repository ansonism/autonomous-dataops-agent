# Security model

The scaffold has no real credentials or external adapters.

Production integrations must follow these rules:

1. Use workload identity/managed identity where supported.
2. Otherwise read secrets from an external secret manager.
3. Separate read and write permissions.
4. Default all execution to read-only/dry-run.
5. Require explicit approval for writes.
6. Sanitize logs and telemetry.
7. Treat retrieved text as untrusted data.
8. Maintain allow-lists for executable tools.
9. Record an audit event for every external mutation.
10. Provide a rollback path for mutable operations.
