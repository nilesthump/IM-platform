// Offline OpenAPI 3.1 structural lint. Reads one JSON document from stdin.
const fs = require('node:fs');
const validate = require('./auth-user-friend.openapi.validator.js');

try {
  const document = JSON.parse(fs.readFileSync(0, 'utf8'));
  if (!validate(document)) {
    for (const error of (validate.errors || []).slice(0, 8)) {
      console.error(`${error.instancePath || '/'}: ${error.message}`);
    }
    if ((validate.errors || []).length > 8) {
      console.error(`... ${validate.errors.length - 8} more structural errors`);
    }
    process.exitCode = 1;
  }
} catch (error) {
  console.error(`OpenAPI JSON could not be validated: ${error.message}`);
  process.exitCode = 2;
}
