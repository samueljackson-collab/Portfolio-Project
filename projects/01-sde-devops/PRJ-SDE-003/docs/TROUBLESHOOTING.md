# Common Issues

- **No internet from private subnets**: Confirm NAT Gateway count and private route table default routes.
- **SSM connectivity fails**: Ensure SSM interface endpoints are enabled and the endpoint security group allows port 443 from app/DB subnets.
- **RDS unreachable**: Validate security group rules permit port 5432 from the web/app SG and that the DB subnet route tables are associated correctly.
- **ALB health check failures**: Check target group health check paths and instance user-data logs.
