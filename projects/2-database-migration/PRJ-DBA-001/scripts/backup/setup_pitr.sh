#!/usr/bin/env bash
set -euo pipefail

: "${WAL_ARCHIVE_DIR:=./wal_archive}"

cat <<CONFIG
Recommended PostgreSQL PITR settings:

archive_mode = on
archive_command = 'test ! -f ${WAL_ARCHIVE_DIR}/%f && cp %p ${WAL_ARCHIVE_DIR}/%f'
wal_level = replica
max_wal_senders = 5
wal_keep_size = 256MB

Recovery command example (postgresql.conf or postgresql.auto.conf on restore target):
restore_command = 'cp ${WAL_ARCHIVE_DIR}/%f %p'
recovery_target = '${PITR_RESTORE_TARGET:-latest}'

Remember to ensure ${WAL_ARCHIVE_DIR} exists and is writable by the postgres user.
CONFIG
