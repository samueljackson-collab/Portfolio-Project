'use strict';

const { handler } = require('../../src/handlers/create');

describe('create handler', () => {
  it('returns 201 with item payload', async () => {
    const event = { body: JSON.stringify({ name: 'test' }), requestContext: { requestId: 'abc-123' } };
    const result = await handler(event);

    expect(result.statusCode).toBe(201);
    const body = JSON.parse(result.body);
    expect(body.message).toBe('Item created');
    expect(body.item.id).toBeDefined();
    expect(body.item.name).toBe('test');
    expect(body.item.persisted).toBe(true);
  });
});
