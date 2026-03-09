SELECT name, setting
FROM pg_settings
WHERE name IN ('log_connections', 'log_disconnections', 'log_line_prefix');
