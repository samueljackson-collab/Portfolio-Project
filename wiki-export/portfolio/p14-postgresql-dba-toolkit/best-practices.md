---
title: Best Practices
description: - Store `.env` outside of version control and use secrets managers for production. - Test restores regularly to validate backups. - Enable `pg_stat_statements` for query performance insights. - Schedu
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/best-practices
created: 2026-03-08T22:19:13.782338+00:00
updated: 2026-03-08T22:04:37.927902+00:00
---

# Best Practices

- Store `.env` outside of version control and use secrets managers for production.
- Test restores regularly to validate backups.
- Enable `pg_stat_statements` for query performance insights.
- Schedule `VACUUM` and `ANALYZE` during low-traffic windows.
- Review role privileges quarterly.
