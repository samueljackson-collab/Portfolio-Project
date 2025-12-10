import { handler as createHandler } from '../../src/handlers/create.js';

const mockSend = jest.fn().mockResolvedValue({});
jest.mock('@aws-sdk/client-dynamodb', () => ({
  DynamoDBClient: jest.fn(() => ({ send: mockSend })),
  PutItemCommand: jest.fn((input) => ({ input })),
}));

jest.mock('uuid', () => ({ v4: () => 'test-id' }));

describe('create handler', () => {
  beforeEach(() => {
    mockSend.mockClear();
  });

  it('creates an item and returns 201', async () => {
    const response = await createHandler({ body: JSON.stringify({ payload: 'hello' }) });

    expect(response.statusCode).toBe(201);
    expect(JSON.parse(response.body)).toMatchObject({ id: 'test-id', message: 'Item created' });
    expect(mockSend).toHaveBeenCalledTimes(1);
  });
});
