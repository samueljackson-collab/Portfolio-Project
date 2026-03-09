# Best Practices

- Store `.env` outside of version control and use secrets managers for production.
- Test restores regularly to validate backups.
- Enable `pg_stat_statements` for query performance insights.
- Schedule `VACUUM` and `ANALYZE` during low-traffic windows.
- Review role privileges quarterly.
