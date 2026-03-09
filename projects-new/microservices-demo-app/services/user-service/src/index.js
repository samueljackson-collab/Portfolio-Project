require('./telemetry');

const express = require('express');
const jwt = require('jsonwebtoken');
const morgan = require('morgan');

const app = express();
app.use(express.json());
app.use(morgan('combined'));

const users = [{ id: 1, email: 'demo@example.com', password: 'password' }];

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'user-service' });
});

app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = users.find((entry) => entry.email === email && entry.password === password);

  if (!user) {
    return res.status(401).json({ error: 'invalid_credentials' });
  }

  const token = jwt.sign({ sub: user.id, email: user.email }, 'demo-secret', { expiresIn: '1h' });
  return res.json({ token });
});

app.get('/auth/profile', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ error: 'missing_token' });
  }

  try {
    const token = authHeader.replace('Bearer ', '');
    const decoded = jwt.verify(token, 'demo-secret');
    return res.json({ id: decoded.sub, email: decoded.email });
  } catch (error) {
    return res.status(401).json({ error: 'invalid_token' });
  }
});

const port = process.env.PORT || 8081;
app.listen(port, () => {
  console.log(`User Service running on ${port}`);
});
