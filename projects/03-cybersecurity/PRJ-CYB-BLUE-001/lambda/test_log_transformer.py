"""
Unit tests for SIEM Log Transformer Lambda function.

Tests transformation logic for GuardDuty, CloudTrail, and VPC Flow Logs.
"""

import json
import base64
from datetime import datetime
import pytest
from log_transformer import (
    lambda_handler,
    transform_guardduty,
    transform_cloudtrail,
    transform_vpc_flow_log,
    map_guardduty_severity,
    determine_cloudtrail_severity,
    map_protocol_number
)


class TestLambdaHandler:
    """Tests for main Lambda handler."""

    def test_lambda_handler_success(self):
        """Test successful processing of records."""
        guardduty_finding = {
            'detail-type': 'GuardDuty Finding',
            'time': '2025-11-06T12:00:00Z',
            'account': '123456789012',
            'region': 'us-east-1',
            'detail': {
                'id': 'test-finding-123',
                'type': 'UnauthorizedAccess:EC2/SSHBruteForce',
                'severity': 8.0,
                'title': 'SSH Brute Force Attack',
                'description': 'Repeated SSH login attempts detected',
                'resource': {'resourceType': 'Instance'}
            }
        }

        event = {
            'records': [
                {
                    'recordId': 'record-1',
                    'data': base64.b64encode(json.dumps(guardduty_finding).encode()).decode()
                }
            ]
        }

        result = lambda_handler(event, None)

        assert len(result['records']) == 1
        assert result['records'][0]['result'] == 'Ok'
        assert result['records'][0]['recordId'] == 'record-1'

    def test_lambda_handler_malformed_record(self):
        """Test handling of malformed records."""
        event = {
            'records': [
                {
                    'recordId': 'record-1',
                    'data': base64.b64encode(b'invalid json {').decode()
                }
            ]
        }

        result = lambda_handler(event, None)

        assert len(result['records']) == 1
        assert result['records'][0]['result'] == 'ProcessingFailed'


class TestGuardDutyTransformation:
    """Tests for GuardDuty log transformation."""

    def test_transform_guardduty_basic(self):
        """Test basic GuardDuty transformation."""
        finding = {
            'detail-type': 'GuardDuty Finding',
            'time': '2025-11-06T12:00:00Z',
            'account': '123456789012',
            'region': 'us-east-1',
            'detail': {
                'id': 'finding-123',
                'type': 'UnauthorizedAccess:EC2/SSHBruteForce',
                'severity': 8.0,
                'title': 'SSH Brute Force',
                'description': 'Repeated SSH attempts',
                'resource': {
                    'resourceType': 'Instance',
                    'instanceDetails': {'instanceId': 'i-1234567890abcdef0'}
                }
            }
        }

        result = transform_guardduty(finding)

        assert result['log_source'] == 'guardduty'
        assert result['event_type'] == 'security_finding'
        assert result['finding_id'] == 'finding-123'
        assert result['severity'] == 'critical'
        assert result['severity_numeric'] == 8.0
        assert result['account_id'] == '123456789012'
        assert result['region'] == 'us-east-1'
        assert result['resource_id'] == 'i-1234567890abcdef0'

    def test_map_guardduty_severity(self):
        """Test severity mapping."""
        assert map_guardduty_severity(8.0) == 'critical'
        assert map_guardduty_severity(5.0) == 'high'
        assert map_guardduty_severity(2.0) == 'medium'
        assert map_guardduty_severity(0.5) == 'low'


class TestCloudTrailTransformation:
    """Tests for CloudTrail log transformation."""

    def test_transform_cloudtrail_basic(self):
        """Test basic CloudTrail transformation."""
        event = {
            'eventVersion': '1.08',
            'eventTime': '2025-11-06T12:00:00Z',
            'eventName': 'CreateBucket',
            'eventSource': 's3.amazonaws.com',
            'eventCategory': 'Management',
            'awsRegion': 'us-east-1',
            'recipientAccountId': '123456789012',
            'sourceIPAddress': '203.0.113.1',
            'userAgent': 'aws-cli/2.0',
            'userIdentity': {
                'type': 'IAMUser',
                'userName': 'testuser',
                'principalId': 'AIDAI23HXSWer4EXAMPLE',
                'arn': 'arn:aws:iam::123456789012:user/testuser',
                'accountId': '123456789012'
            },
            'requestID': 'req-123'
        }

        result = transform_cloudtrail(event)

        assert result['log_source'] == 'cloudtrail'
        assert result['event_type'] == 'api_call'
        assert result['event_name'] == 'CreateBucket'
        assert result['event_source'] == 's3.amazonaws.com'
        assert result['user_name'] == 'testuser'
        assert result['source_ip'] == '203.0.113.1'
        assert result['account_id'] == '123456789012'

    def test_determine_cloudtrail_severity_root(self):
        """Test severity for root user actions."""
        event = {
            'eventName': 'ListBuckets',
            'userIdentity': {'type': 'Root'}
        }

        severity = determine_cloudtrail_severity(event)
        assert severity == 'critical'

    def test_determine_cloudtrail_severity_delete(self):
        """Test severity for delete operations."""
        event = {
            'eventName': 'DeleteBucket',
            'userIdentity': {'type': 'IAMUser'}
        }

        severity = determine_cloudtrail_severity(event)
        assert severity == 'high'

    def test_determine_cloudtrail_severity_access_denied(self):
        """Test severity for access denied."""
        event = {
            'eventName': 'GetObject',
            'userIdentity': {'type': 'IAMUser'},
            'errorCode': 'AccessDenied'
        }

        severity = determine_cloudtrail_severity(event)
        assert severity == 'medium'


class TestVPCFlowLogTransformation:
    """Tests for VPC Flow Log transformation."""

    def test_transform_vpc_flow_log_accept(self):
        """Test VPC Flow Log transformation for accepted traffic."""
        log_entry = {
            'version': '2',
            'account-id': '123456789012',
            'interface-id': 'eni-1234567890abcdef0',
            'srcaddr': '10.0.1.5',
            'dstaddr': '10.0.2.10',
            'srcport': 50123,
            'dstport': 443,
            'protocol': 6,
            'packets': 10,
            'bytes': 5000,
            'start': 1699272000,
            'end': 1699272060,
            'action': 'ACCEPT',
            'log-status': 'OK',
            'region': 'us-east-1'
        }

        result = transform_vpc_flow_log(log_entry)

        assert result['log_source'] == 'vpc_flow_log'
        assert result['event_type'] == 'network_traffic'
        assert result['source_ip'] == '10.0.1.5'
        assert result['destination_ip'] == '10.0.2.10'
        assert result['source_port'] == 50123
        assert result['destination_port'] == 443
        assert result['protocol'] == 'TCP'
        assert result['protocol_number'] == 6
        assert result['action'] == 'ACCEPT'
        assert result['severity'] == 'info'
        assert result['bytes'] == 5000
        assert result['packets'] == 10

    def test_transform_vpc_flow_log_reject(self):
        """Test VPC Flow Log transformation for rejected traffic."""
        log_entry = {
            'srcaddr': '203.0.113.1',
            'dstaddr': '10.0.1.5',
            'srcport': 12345,
            'dstport': 22,
            'protocol': 6,
            'packets': 1,
            'bytes': 40,
            'start': 1699272000,
            'end': 1699272000,
            'action': 'REJECT',
            'log-status': 'OK'
        }

        result = transform_vpc_flow_log(log_entry)

        assert result['action'] == 'REJECT'
        assert result['severity'] == 'warning'

    def test_map_protocol_number(self):
        """Test protocol number mapping."""
        assert map_protocol_number(1) == 'ICMP'
        assert map_protocol_number(6) == 'TCP'
        assert map_protocol_number(17) == 'UDP'
        assert map_protocol_number(58) == 'ICMPv6'
        assert map_protocol_number(99) == '99'


class TestIntegration:
    """Integration tests for end-to-end processing."""

    def test_process_mixed_logs(self):
        """Test processing different log types in single batch."""
        guardduty_log = {
            'detail-type': 'GuardDuty Finding',
            'time': '2025-11-06T12:00:00Z',
            'account': '123456789012',
            'region': 'us-east-1',
            'detail': {
                'id': 'gd-123',
                'type': 'Recon:EC2/PortProbeUnprotectedPort',
                'severity': 5.0,
                'title': 'Port Scan',
                'description': 'Port scanning detected'
            }
        }

        cloudtrail_log = {
            'eventVersion': '1.08',
            'eventTime': '2025-11-06T12:00:00Z',
            'eventName': 'DescribeInstances',
            'eventSource': 'ec2.amazonaws.com',
            'awsRegion': 'us-east-1',
            'recipientAccountId': '123456789012',
            'userIdentity': {'type': 'IAMUser', 'userName': 'admin'}
        }

        vpc_flow_log = {
            'srcaddr': '10.0.1.5',
            'dstaddr': '10.0.2.10',
            'srcport': 443,
            'dstport': 80,
            'protocol': 6,
            'action': 'ACCEPT',
            'bytes': 1500,
            'packets': 5,
            'start': 1699272000,
            'end': 1699272060
        }

        event = {
            'records': [
                {
                    'recordId': 'gd-1',
                    'data': base64.b64encode(json.dumps(guardduty_log).encode()).decode()
                },
                {
                    'recordId': 'ct-1',
                    'data': base64.b64encode(json.dumps(cloudtrail_log).encode()).decode()
                },
                {
                    'recordId': 'vpc-1',
                    'data': base64.b64encode(json.dumps(vpc_flow_log).encode()).decode()
                }
            ]
        }

        result = lambda_handler(event, None)

        assert len(result['records']) == 3
        assert all(r['result'] == 'Ok' for r in result['records'])

        # Decode and verify each log type
        for record in result['records']:
            decoded = json.loads(base64.b64decode(record['data']).decode())
            assert '@timestamp' in decoded
            assert 'log_source' in decoded
            assert 'severity' in decoded


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
