require('./telemetry');

const express = require('express');
const axios = require('axios');
const morgan = require('morgan');
const promClient = require('prom-client');

const app = express();
const register = new promClient.Registry();

register.setDefaultLabels({ service: 'api-gateway' });
promClient.collectDefaultMetrics({ register });

app.use(express.json());
app.use(morgan('combined'));

const serviceRoutes = [
  { prefix: '/users', target: process.env.USER_SERVICE_URL },
  { prefix: '/products', target: process.env.PRODUCT_SERVICE_URL },
  { prefix: '/orders', target: process.env.ORDER_SERVICE_URL },
  { prefix: '/payments', target: process.env.PAYMENT_SERVICE_URL },
  { prefix: '/notifications', target: process.env.NOTIFICATION_SERVICE_URL },
];

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'api-gateway' });
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.send(await register.metrics());
});

app.all('*', async (req, res) => {
  const route = serviceRoutes.find((entry) => req.path.startsWith(entry.prefix));
  if (!route || !route.target) {
    return res.status(404).json({ error: 'route not found' });
  }

  try {
    const response = await axios({
      method: req.method,
      url: `${route.target}${req.path}`,
      data: req.body,
      params: req.query,
      headers: {
        'x-request-id': req.headers['x-request-id'] || '',
      },
    });

    return res.status(response.status).json(response.data);
  } catch (error) {
    const status = error.response?.status || 500;
    return res.status(status).json({
      error: 'upstream_error',
      message: error.response?.data || error.message,
    });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`API Gateway running on ${port}`);
});
