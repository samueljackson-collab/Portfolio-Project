import { DynamoDBClient, GetItemCommand } from '@aws-sdk/client-dynamodb';

const dynamo = new DynamoDBClient({});
const TABLE_NAME = process.env.TABLE_NAME;

export const handler = async (event) => {
  try {
    const id = event.pathParameters?.id;
    if (!id) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Missing id parameter' }) };
    }

    const result = await dynamo.send(
      new GetItemCommand({
        TableName: TABLE_NAME,
        Key: { id: { S: id } },
        ConsistentRead: true,
      })
    );

    if (!result.Item) {
      return { statusCode: 404, body: JSON.stringify({ error: 'Item not found' }) };
    }

    const item = {
      id: result.Item.id.S,
      payload: result.Item.payload?.S,
      createdAt: result.Item.createdAt?.S,
    };

    return {
      statusCode: 200,
      body: JSON.stringify(item),
    };
  } catch (error) {
    console.error('Read handler error', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to read item' }),
    };
  }
};
