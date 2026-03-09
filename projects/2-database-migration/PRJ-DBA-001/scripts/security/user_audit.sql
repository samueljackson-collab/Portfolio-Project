SELECT usename,
       usesuper,
       usecreatedb,
       valuntil,
       rolname
FROM pg_user
LEFT JOIN pg_auth_members ON pg_user.usesysid = pg_auth_members.member
LEFT JOIN pg_roles ON pg_auth_members.roleid = pg_roles.oid
ORDER BY usename;
