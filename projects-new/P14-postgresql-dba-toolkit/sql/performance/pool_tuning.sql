SELECT
  name,
  setting,
  unit
FROM pg_settings
WHERE name IN ('max_connections', 'superuser_reserved_connections', 'shared_buffers', 'work_mem');
