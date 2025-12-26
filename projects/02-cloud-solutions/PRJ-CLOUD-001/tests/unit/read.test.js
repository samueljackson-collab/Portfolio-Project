import { handler as readHandler } from '../../src/handlers/read.js';

const mockSend = jest.fn();
jest.mock('@aws-sdk/client-dynamodb', () => ({
  DynamoDBClient: jest.fn(() => ({ send: mockSend })),
  GetItemCommand: jest.fn((input) => ({ input })),
}));

describe('read handler', () => {
  beforeEach(() => {
    mockSend.mockReset();
  });

  it('returns 400 when id is missing', async () => {
    const response = await readHandler({ pathParameters: {} });
    expect(response.statusCode).toBe(400);
  });

  it('returns 404 when item does not exist', async () => {
    mockSend.mockResolvedValueOnce({});
    const response = await readHandler({ pathParameters: { id: 'missing' } });
    expect(response.statusCode).toBe(404);
  });
});
