const express = require('express');
const app = express();
app.use(express.json());

app.post('/auth/token', (req, res) => {
  const { client_id, client_secret } = req.body;
  if (client_id === 'demo' && client_secret === 'secret') {
    return res.json({ access_token: 'fake-jwt', expires_in: 3600 });
  }
  return res.status(401).json({ error: 'invalid_client' });
});

app.get('/orders', (req, res) => {
  const pageSize = parseInt(req.query.pageSize || '20', 10);
  const items = Array.from({ length: pageSize }, (_, i) => ({ id: i + 1, total: 42.5 }));
  res.json({ items, pageInfo: { next: '/orders?page=3' } });
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Mock API listening on ${port}`));
