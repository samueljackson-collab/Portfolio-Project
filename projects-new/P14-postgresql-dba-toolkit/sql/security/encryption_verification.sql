SELECT name, setting
FROM pg_settings
WHERE name IN ('ssl', 'ssl_min_protocol_version', 'ssl_max_protocol_version');
