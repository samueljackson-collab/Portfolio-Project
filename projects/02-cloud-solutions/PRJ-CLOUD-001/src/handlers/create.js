'use strict';

const { randomUUID } = require('crypto');

const log = (level, message, context = {}) => {
  console.log(JSON.stringify({ level, message, ...context }));
};

const response = (statusCode, body) => ({
  statusCode,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

module.exports.handler = async (event) => {
  log('INFO', 'Received create request', { requestId: event?.requestContext?.requestId });

  const timestamp = new Date().toISOString();
  const payload = typeof event.body === 'string' ? JSON.parse(event.body || '{}') : event.body || {};
  const id = randomUUID();

  const item = {
    id,
    name: payload.name || 'unnamed',
    createdAt: timestamp,
    metadata: payload.metadata || {},
  };

  log('DEBUG', 'Prepared item for persistence', { item });

  // Placeholder for DynamoDB persistence call; mocked for portfolio demonstration.
  const saved = { ...item, persisted: true };

  return response(201, { message: 'Item created', item: saved });
};
