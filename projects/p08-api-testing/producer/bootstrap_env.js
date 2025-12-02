const fs = require('fs');
const path = require('path');

const env = {
  id: 'p08-local',
  name: 'p08-local',
  values: [
    { key: 'baseUrl', value: 'http://localhost:1080', enabled: true },
    { key: 'apiKey', value: 'changeme', enabled: true },
  ],
};

const outDir = path.join(__dirname, '..', 'artifacts');
fs.mkdirSync(outDir, { recursive: true });
const outFile = path.join(outDir, 'local.postman_environment.json');
fs.writeFileSync(outFile, JSON.stringify(env, null, 2));
console.log(`Wrote ${outFile}`);
