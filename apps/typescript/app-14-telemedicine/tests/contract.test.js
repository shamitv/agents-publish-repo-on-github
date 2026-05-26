const assert = require("assert");
const fs = require("fs");
const path = require("path");

const appRoot = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(appRoot, relativePath), "utf8");
const exists = (relativePath) => fs.existsSync(path.join(appRoot, relativePath));

assert.ok(exists("src/controllers/AppointmentController.ts"));
assert.ok(exists("src/services/AppointmentService.ts"));
assert.ok(exists("src/services/TokenService.ts"));
assert.ok(exists("src/repositories/AppointmentRepository.ts"));
assert.ok(exists("src/db/InMemoryMedicalDatabase.ts"));
assert.ok(exists("src/cache/AppointmentCache.ts"));
assert.ok(exists("src/mq/AuditEventProducer.ts"));
assert.ok(exists("src/search/PatientSearchClient.ts"));

const entrypoint = read("src/index.ts");
assert.ok(entrypoint.includes("createApp"));
assert.ok(!entrypoint.includes("app.get("));
assert.ok(!entrypoint.includes("jwt.decode("));

const manifest = JSON.parse(read(".vulns"));
const chain = manifest.chained_attacks[0];
assert.equal(chain.chain_id, "chain-01");
assert.equal(chain.impact, "db_exfiltration");
assert.equal(chain.components.length, 2);
assert.equal(chain.components[0].method, "verify");
assert.equal(chain.components[1].method, "getAppointmentDetail");

assert.ok(read("src/services/TokenService.ts").includes("CHAIN LINK 1 (chain-01)"));
assert.ok(read("src/services/AppointmentService.ts").includes("CHAIN LINK 2 (chain-01)"));
assert.ok(read("src/controllers/AuthController.ts").includes("VULNERABILITY A07"));

console.log("app-14 contract checks passed");
