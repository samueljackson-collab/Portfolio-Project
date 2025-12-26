const request = require('supertest');

describe('API Gateway', () => {
  let server;

  beforeAll(() => {
    server = require('http').createServer(require('express')().get('/health', (req, res) => {
      res.json({ status: 'ok' });
    }));
  });

  it('responds with ok', async () => {
    const response = await request(server).get('/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('ok');
  });
});
