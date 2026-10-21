// Offline OpenAPI 3.1 structural lint. Reads one JSON document from stdin.
const fs = require('node:fs');
const validate = require('./auth-user-friend.openapi.validator.js');

try {
  // Strip a leading UTF-8 BOM: Windows PowerShell 5.1 pipeline stdin prepends
  // one (contract verifier + documented standalone usage pipe JSON to stdin).
  const raw = fs.readFileSync(0, 'utf8').replace(/^\uFEFF/, '');
  const document = JSON.parse(raw);
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
