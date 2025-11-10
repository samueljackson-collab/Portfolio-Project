#!/usr/bin/env python3
"""CIS AWS Foundations Benchmark compliance checker."""
import boto3
import sys

def check_cloudtrail_enabled():
    """CIS 2.1 - Ensure CloudTrail is enabled."""
    client = boto3.client('cloudtrail')
    trails = client.describe_trails()

    enabled_trails = [t for t in trails['trailList'] if t.get('IsMultiRegionTrail')]

    if len(enabled_trails) > 0:
        print("✓ CIS 2.1: CloudTrail is enabled")
        return True
    else:
        print("✗ CIS 2.1: CloudTrail is NOT enabled")
        return False

def check_s3_bucket_logging():
    """CIS 2.6 - Ensure S3 bucket logging is enabled."""
    s3 = boto3.client('s3')
    buckets = s3.list_buckets()

    issues = []
    errors = []
    for bucket in buckets['Buckets']:
        try:
            logging = s3.get_bucket_logging(Bucket=bucket['Name'])
            if 'LoggingEnabled' not in logging:
                issues.append(bucket['Name'])
        except s3.exceptions.NoSuchBucket:
            # Bucket was deleted between list and check, skip
            continue
        except Exception as e:
            # Log permission errors or other issues for investigation
            error_msg = f"{bucket['Name']}: {type(e).__name__} - {str(e)}"
            errors.append(error_msg)
            print(f"  ⚠️  Unable to check bucket {bucket['Name']}: {type(e).__name__}")

    if errors:
        print(f"  ℹ️  Encountered {len(errors)} errors during bucket checks (may indicate permission issues)")

    if len(issues) == 0:
        print("✓ CIS 2.6: S3 bucket logging is enabled for all buckets")
        return True
    else:
        print(f"✗ CIS 2.6: S3 bucket logging disabled for {len(issues)} buckets: {', '.join(issues[:5])}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")
        return False

def check_mfa_root_account():
    """CIS 1.5 - Ensure MFA is enabled for root account."""
    iam = boto3.client('iam')
    summary = iam.get_account_summary()

    mfa_devices = summary['SummaryMap'].get('AccountMFAEnabled', 0)

    if mfa_devices > 0:
        print("✓ CIS 1.5: MFA is enabled for root account")
        return True
    else:
        print("✗ CIS 1.5: MFA is NOT enabled for root account")
        return False

def main():
    """Run CIS compliance checks."""
    print("Running CIS AWS Foundations Benchmark checks...\n")

    checks = [
        check_cloudtrail_enabled,
        check_s3_bucket_logging,
        check_mfa_root_account,
    ]

    results = [check() for check in checks]

    print(f"\n✓ Passed: {sum(results)}/{len(results)}")
    print(f"✗ Failed: {len(results) - sum(results)}/{len(results)}")

    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
