const fs = require('fs');
const path = require('path');

const reportPath = path.join(__dirname, '..', 'reports', 'newman', 'results.json');
if (!fs.existsSync(reportPath)) {
  console.error('Report missing, run tests first');
  process.exit(1);
}
const data = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
const summary = {
  totalRequests: data.run.stats.requests.total,
  totalFailures: data.run.stats.requests.failed,
  meanLatencyMs: data.run.timings.responseAverage,
};
const outFile = path.join(__dirname, '..', 'reports', 'summary.json');
fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
