"""
AWS SIEM Log Transformer for Kinesis Firehose

This Lambda function transforms and normalizes security logs from multiple
AWS sources (GuardDuty, VPC Flow Logs, CloudTrail) into a common schema
for ingestion into OpenSearch.

Input: Kinesis Firehose records
Output: Transformed records with common schema
"""

import base64
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Common schema field names
COMMON_SCHEMA = {
    'timestamp': '@timestamp',
    'severity': 'severity',
    'source': 'log_source',
    'account_id': 'account_id',
    'region': 'region',
    'event_type': 'event_type',
    'message': 'message'
}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Transform Kinesis Firehose records into a normalized schema for OpenSearch ingestion.
    
    Processes each record from the incoming Firehose event, decodes and parses the record data, applies source-specific normalization, and returns a list of transformed records. Records that fail processing are returned with result 'ProcessingFailed' and their original data preserved for retry or S3 backup.
    
    Parameters:
        event (dict): Kinesis Firehose event payload containing a 'records' list; each record must include 'recordId' and base64-encoded 'data'.
        context (Any): AWS Lambda context object (not used by this function).
    
    Returns:
        dict: A dictionary with a 'records' key mapping to a list of output records. Each output record contains:
            - 'recordId' (str): the original record identifier.
            - 'result' (str): 'Ok' for successfully transformed records or 'ProcessingFailed' for errors.
            - 'data' (str): base64-encoded transformed JSON (with trailing newline) for successful records, or the original input data for failed records.
    """
    logger.info(f"Processing {len(event['records'])} records")

    output_records = []

    for record in event['records']:
        try:
            # Decode the incoming record
            payload = base64.b64decode(record['data']).decode('utf-8')
            log_entry = json.loads(payload)

            # Determine log source and transform accordingly
            transformed_log = transform_log(log_entry)

            # Encode the transformed log
            output_data = json.dumps(transformed_log) + '\n'
            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(output_data.encode('utf-8')).decode('utf-8')
            }

            output_records.append(output_record)

        except Exception as e:
            logger.error(f"Error processing record {record['recordId']}: {str(e)}")
            # Mark as failed but allow Firehose to retry or send to S3 backup
            output_records.append({
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            })

    logger.info(f"Successfully processed {sum(1 for r in output_records if r['result'] == 'Ok')} records")

    return {'records': output_records}


def transform_log(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route a raw AWS log entry to the appropriate source-specific transformer and return a normalized record.
    
    If the entry matches GuardDuty, CloudTrail, or VPC Flow Log patterns this delegates to the corresponding transformer; otherwise returns a minimal common-schema record with source set to 'unknown'.
    
    Parameters:
        log_entry (Dict[str, Any]): The original parsed log payload.
    
    Returns:
        Dict[str, Any]: A normalized log record conforming to the module's common schema. For unknown formats the returned record will include `log_source` set to `'unknown'`.
    """
    # Detect log source
    if 'detail-type' in log_entry and 'GuardDuty Finding' in log_entry.get('detail-type', ''):
        return transform_guardduty(log_entry)
    elif 'eventVersion' in log_entry and 'eventName' in log_entry:
        return transform_cloudtrail(log_entry)
    elif 'srcaddr' in log_entry or 'dstaddr' in log_entry:
        return transform_vpc_flow_log(log_entry)
    else:
        # Unknown format - pass through with minimal transformation
        return add_common_fields(log_entry, 'unknown')


def transform_guardduty(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a GuardDuty finding into the module's common schema.
    
    Parameters:
        log_entry (dict): Raw GuardDuty event payload (expected to contain a top-level "detail" object).
    
    Returns:
        dict: Normalized record containing common schema fields (timestamps, log_source, event_type, account_id, region),
        GuardDuty-specific fields (finding_id, finding_type, severity, severity_numeric, title, description, message),
        resource and actor information (resource_type, resource_id, source_ip, source_country), service metadata (service_action, service_count),
        and the original finding under `raw_finding`.
    """
    detail = log_entry.get('detail', {})

    transformed = {
        '@timestamp': log_entry.get('time', datetime.utcnow().isoformat()),
        'log_source': 'guardduty',
        'event_type': 'security_finding',
        'account_id': log_entry.get('account', 'unknown'),
        'region': log_entry.get('region', 'unknown'),

        # GuardDuty specific fields
        'finding_id': detail.get('id'),
        'finding_type': detail.get('type'),
        'severity': map_guardduty_severity(detail.get('severity', 0)),
        'severity_numeric': detail.get('severity', 0),
        'title': detail.get('title'),
        'description': detail.get('description'),
        'message': detail.get('title', 'GuardDuty Finding'),

        # Resource information
        'resource_type': detail.get('resource', {}).get('resourceType'),
        'resource_id': extract_resource_id(detail.get('resource', {})),

        # Service information
        'service_action': detail.get('service', {}).get('action'),
        'service_count': detail.get('service', {}).get('count', 0),

        # Actor information
        'source_ip': extract_source_ip(detail),
        'source_country': extract_source_country(detail),

        # Original data
        'raw_finding': detail
    }

    return transformed


def transform_cloudtrail(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a CloudTrail event into the module's common schema.
    
    Parameters:
        log_entry (Dict[str, Any]): Parsed CloudTrail event payload.
    
    Returns:
        Dict[str, Any]: Dictionary containing CloudTrail fields mapped to the common schema, including metadata (timestamp, account, region), user identity, source/request details, computed severity, resources, and the original event under `raw_event`.
    """
    transformed = {
        '@timestamp': log_entry.get('eventTime', datetime.utcnow().isoformat()),
        'log_source': 'cloudtrail',
        'event_type': 'api_call',
        'account_id': log_entry.get('recipientAccountId', 'unknown'),
        'region': log_entry.get('awsRegion', 'unknown'),

        # CloudTrail specific fields
        'event_name': log_entry.get('eventName'),
        'event_source': log_entry.get('eventSource'),
        'event_category': log_entry.get('eventCategory'),
        'message': f"{log_entry.get('eventName', 'API Call')} by {log_entry.get('userIdentity', {}).get('principalId', 'unknown')}",

        # User identity
        'user_type': log_entry.get('userIdentity', {}).get('type'),
        'user_name': log_entry.get('userIdentity', {}).get('userName'),
        'user_principal_id': log_entry.get('userIdentity', {}).get('principalId'),
        'user_arn': log_entry.get('userIdentity', {}).get('arn'),
        'user_account_id': log_entry.get('userIdentity', {}).get('accountId'),

        # Source information
        'source_ip': log_entry.get('sourceIPAddress'),
        'user_agent': log_entry.get('userAgent'),

        # Request/response
        'error_code': log_entry.get('errorCode'),
        'error_message': log_entry.get('errorMessage'),
        'request_id': log_entry.get('requestID'),

        # Severity mapping
        'severity': determine_cloudtrail_severity(log_entry),

        # Resources
        'resources': log_entry.get('resources', []),

        # Original data
        'raw_event': log_entry
    }

    return transformed


def transform_vpc_flow_log(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a VPC Flow Log (JSON dict or space-delimited string) into the transformer's common schema.
    
    Parameters:
        log_entry (dict | str): VPC Flow Log as a parsed dictionary or a space-delimited log line string; when a string is provided it will be parsed into a dict.
    
    Returns:
        dict: Normalized VPC Flow Log containing canonical fields such as '@timestamp', 'log_source', 'event_type', 'account_id', 'region', network fields ('source_ip', 'destination_ip', 'source_port', 'destination_port', 'protocol', 'protocol_number'), traffic metrics ('bytes', 'packets'), 'action', 'log_status', interface info, 'severity', human-readable 'message', 'start_time', 'end_time', and the original data under 'raw_log'.
    """
    # VPC Flow Logs can be in different formats; handle both JSON and space-delimited
    if isinstance(log_entry, str):
        log_entry = parse_vpc_flow_log_string(log_entry)

    action = log_entry.get('action', 'UNKNOWN')

    transformed = {
        '@timestamp': convert_flow_log_timestamp(log_entry.get('start', 0)),
        'log_source': 'vpc_flow_log',
        'event_type': 'network_traffic',
        'account_id': log_entry.get('account-id', 'unknown'),
        'region': log_entry.get('region', 'unknown'),

        # Network information
        'source_ip': log_entry.get('srcaddr'),
        'source_port': log_entry.get('srcport'),
        'destination_ip': log_entry.get('dstaddr'),
        'destination_port': log_entry.get('dstport'),
        'protocol': map_protocol_number(log_entry.get('protocol', 0)),
        'protocol_number': log_entry.get('protocol'),

        # Traffic metrics
        'bytes': log_entry.get('bytes', 0),
        'packets': log_entry.get('packets', 0),
        'action': action,
        'log_status': log_entry.get('log-status', 'OK'),

        # Interface information
        'interface_id': log_entry.get('interface-id'),

        # Severity
        'severity': 'info' if action == 'ACCEPT' else 'warning',
        'message': f"Network traffic from {log_entry.get('srcaddr')} to {log_entry.get('dstaddr')} - {action}",

        # Timestamps
        'start_time': convert_flow_log_timestamp(log_entry.get('start', 0)),
        'end_time': convert_flow_log_timestamp(log_entry.get('end', 0)),

        # Original data
        'raw_log': log_entry
    }

    return transformed


# Helper functions

def add_common_fields(log_entry: Dict[str, Any], source: str) -> Dict[str, Any]:
    """
    Create a minimal normalized record for logs with an unknown or unsupported format.
    
    Parameters:
        log_entry (dict): The original parsed log payload to preserve as `raw_log`.
        source (str): Identifier for the log source to set the `log_source` field.
    
    Returns:
        dict: A normalized record containing:
            - '@timestamp': ISO UTC timestamp when the record was created.
            - 'log_source': the provided source identifier.
            - 'event_type': set to 'unknown'.
            - 'severity': set to 'info'.
            - 'message': brief description ('Unknown log format').
            - 'raw_log': the original `log_entry`.
    """
    return {
        '@timestamp': datetime.utcnow().isoformat(),
        'log_source': source,
        'event_type': 'unknown',
        'severity': 'info',
        'message': 'Unknown log format',
        'raw_log': log_entry
    }


def map_guardduty_severity(severity_numeric: float) -> str:
    """
    Convert a GuardDuty numeric severity score into a textual severity level.
    
    Returns:
        str: `'critical'` if severity_numeric >= 7.0, `'high'` if severity_numeric >= 4.0, `'medium'` if severity_numeric >= 1.0, `'low'` otherwise.
    """
    if severity_numeric >= 7.0:
        return 'critical'
    elif severity_numeric >= 4.0:
        return 'high'
    elif severity_numeric >= 1.0:
        return 'medium'
    else:
        return 'low'


def extract_resource_id(resource: Dict[str, Any]) -> str:
    """
    Extract a representative identifier for the resource described in a GuardDuty resource object.
    
    Parameters:
        resource (Dict[str, Any]): GuardDuty resource dictionary (as found in a finding's `resource` field).
    
    Returns:
        str: The extracted identifier — `instanceId` if present under `instanceDetails`, otherwise `accessKeyId` if present under `accessKeyDetails`, otherwise the `resourceType` value, or `'unknown'` if none are available.
    """
    instance_details = resource.get('instanceDetails', {})
    if instance_details:
        return instance_details.get('instanceId', 'unknown')

    access_key_details = resource.get('accessKeyDetails', {})
    if access_key_details:
        return access_key_details.get('accessKeyId', 'unknown')

    return resource.get('resourceType', 'unknown')


def extract_source_ip(detail: Dict[str, Any]) -> str:
    """
    Extracts the source IPv4 address from a GuardDuty finding detail.
    
    Parameters:
        detail (dict): GuardDuty finding `detail` object expected to contain `service.action.networkConnectionAction.remoteIpDetails.ipAddressV4`
            or `service.action.awsApiCallAction.remoteIpDetails.ipAddressV4`.
    
    Returns:
        str: The extracted IPv4 address if present, `"unknown"` otherwise.
    """
    service = detail.get('service', {})
    action = service.get('action', {})

    # Try network connection action
    network_connection = action.get('networkConnectionAction', {})
    if network_connection:
        remote_ip_details = network_connection.get('remoteIpDetails', {})
        return remote_ip_details.get('ipAddressV4', 'unknown')

    # Try AWS API call action
    aws_api_call = action.get('awsApiCallAction', {})
    if aws_api_call:
        remote_ip_details = aws_api_call.get('remoteIpDetails', {})
        return remote_ip_details.get('ipAddressV4', 'unknown')

    return 'unknown'


def extract_source_country(detail: Dict[str, Any]) -> str:
    """
    Determine the source country name from a GuardDuty finding detail.
    
    Parameters:
        detail (dict): The GuardDuty finding `detail` payload to inspect.
    
    Returns:
        country_name (str): The country name from `detail.service.action.*.remoteIpDetails.country.countryName` if present, otherwise `'unknown'`.
    """
    service = detail.get('service', {})
    action = service.get('action', {})

    for action_type in ['networkConnectionAction', 'awsApiCallAction']:
        action_details = action.get(action_type, {})
        if action_details:
            remote_ip_details = action_details.get('remoteIpDetails', {})
            country = remote_ip_details.get('country', {})
            return country.get('countryName', 'unknown')

    return 'unknown'


def determine_cloudtrail_severity(event: Dict[str, Any]) -> str:
    """
    Infer severity level for a CloudTrail event.
    
    Parameters:
        event (Dict[str, Any]): CloudTrail event dictionary.
    
    Returns:
        str: 'critical' if the event was performed by the root user; 'high' if the event name indicates deletion/removal/termination; 'medium' for failed authentication/authorization error codes; 'warning' for other error codes; 'info' otherwise.
    """
    event_name = event.get('eventName', '').lower()
    error_code = event.get('errorCode')
    user_identity = event.get('userIdentity', {})

    # Critical events
    if user_identity.get('type') == 'Root':
        return 'critical'

    if 'delete' in event_name or 'remove' in event_name or 'terminate' in event_name:
        return 'high'

    # Failed authentication
    if error_code in ['AccessDenied', 'UnauthorizedOperation', 'InvalidClientTokenId']:
        return 'medium'

    # Errors
    if error_code:
        return 'warning'

    # Normal operations
    return 'info'


def parse_vpc_flow_log_string(log_string: str) -> Dict[str, Any]:
    """
    Parse a space-delimited VPC Flow Log line into a dictionary of standard fields.
    
    Parameters:
        log_string (str): A single VPC Flow Log record as a whitespace-delimited string.
    
    Returns:
        Dict[str, Any]: Mapping of VPC Flow Log field names ('version', 'account-id', 'interface-id', 'srcaddr', 'dstaddr', 'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'start', 'end', 'action', 'log-status') to their corresponding string values. Extra tokens are ignored and missing tokens result in omitted keys due to simple zipping.
    """
    # Standard VPC Flow Log format
    fields = ['version', 'account-id', 'interface-id', 'srcaddr', 'dstaddr',
              'srcport', 'dstport', 'protocol', 'packets', 'bytes',
              'start', 'end', 'action', 'log-status']

    values = log_string.strip().split()

    return dict(zip(fields, values))


def convert_flow_log_timestamp(unix_timestamp: Any) -> str:
    """
    Convert a VPC Flow Log UNIX timestamp (seconds) to an ISO 8601 UTC timestamp string.
    
    Accepts an integer or numeric string representing seconds since the Unix epoch and returns its UTC ISO 8601 representation. If the input is not a valid integer, returns the current UTC time in ISO 8601 format.
    
    Parameters:
        unix_timestamp (Any): UNIX timestamp in seconds (int or numeric string).
    
    Returns:
        str: ISO 8601 formatted UTC timestamp (e.g., "2025-11-06T12:34:56").
    """
    try:
        timestamp = int(unix_timestamp)
        return datetime.utcfromtimestamp(timestamp).isoformat()
    except (ValueError, TypeError):
        return datetime.utcnow().isoformat()


def map_protocol_number(protocol_num: Any) -> str:
    """
    Convert an IP protocol number into its common protocol name.
    
    Parameters:
        protocol_num (Any): Numeric protocol identifier or a value convertible to int (e.g., 6 or "6").
    
    Returns:
        str: The mapped protocol name (`'ICMP'`, `'TCP'`, `'UDP'`, `'ICMPv6'`) if known; the string form of `protocol_num` if not recognized; `'UNKNOWN'` if `protocol_num` cannot be interpreted as an integer.
    """
    protocol_map = {
        1: 'ICMP',
        6: 'TCP',
        17: 'UDP',
        58: 'ICMPv6'
    }

    try:
        return protocol_map.get(int(protocol_num), str(protocol_num))
    except (ValueError, TypeError):
        return 'UNKNOWN'