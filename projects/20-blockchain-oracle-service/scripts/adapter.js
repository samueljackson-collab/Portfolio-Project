const express = require('express');
const bodyParser = require('body-parser');
const app = express();
app.use(bodyParser.json());

app.post('/', (req, res) => {
  const metric = 9200; // Example metric from monitoring stack
  res.json({
    jobRunID: req.body.id,
    data: { result: metric },
    result: metric,
    statusCode: 200
  });
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Oracle adapter listening on ${port}`));
