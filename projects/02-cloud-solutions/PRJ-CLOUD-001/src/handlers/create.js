import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';
import { v4 as uuidv4 } from 'uuid';

const dynamo = new DynamoDBClient({});
const TABLE_NAME = process.env.TABLE_NAME;

export const handler = async (event) => {
  try {
    const body = JSON.parse(event.body || '{}');
    const id = uuidv4();
    const item = {
      id: { S: id },
      payload: { S: body.payload || 'default' },
      createdAt: { S: new Date().toISOString() },
    };

    await dynamo.send(
      new PutItemCommand({
        TableName: TABLE_NAME,
        Item: item,
        ConditionExpression: 'attribute_not_exists(id)',
      })
    );

    return {
      statusCode: 201,
      body: JSON.stringify({ id, message: 'Item created' }),
    };
  } catch (error) {
    console.error('Create handler error', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to create item' }),
    };
  }
};
