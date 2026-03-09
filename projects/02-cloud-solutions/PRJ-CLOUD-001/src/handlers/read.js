'use strict';

const log = (level, message, context = {}) => {
  console.log(JSON.stringify({ level, message, ...context }));
};

const response = (statusCode, body) => ({
  statusCode,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

module.exports.handler = async (event) => {
  log('INFO', 'Received read request', { requestId: event?.requestContext?.requestId });

  const id = event?.pathParameters?.id;
  if (!id) {
    log('WARN', 'Missing path parameter: id');
    return response(400, { message: 'Item id is required' });
  }

  // Placeholder for DynamoDB getItem call; returning mock data for portfolio purposes.
  const item = {
    id,
    name: 'example',
    createdAt: '2024-01-01T00:00:00.000Z',
    metadata: { source: 'mock' },
  };

  log('DEBUG', 'Retrieved item', { item });

  return response(200, { message: 'Item retrieved', item });
};
