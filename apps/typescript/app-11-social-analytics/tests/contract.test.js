const assert = require("assert");
const fs = require("fs");
const path = require("path");

const appRoot = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(appRoot, relativePath), "utf8");
const exists = (relativePath) => fs.existsSync(path.join(appRoot, relativePath));

assert.ok(exists("src/controllers/PreviewController.ts"));
assert.ok(exists("src/services/PreviewService.ts"));
assert.ok(exists("src/repositories/WidgetRepository.ts"));
assert.ok(exists("src/db/InMemoryDatabase.ts"));
assert.ok(exists("src/cache/SessionCache.ts"));
assert.ok(exists("src/mq/AnalyticsEventProducer.ts"));
assert.ok(exists("src/mq/AnalyticsEventConsumer.ts"));
assert.ok(exists("src/search/InternalSearchClient.ts"));

const entrypoint = read("src/index.ts");
assert.ok(entrypoint.includes("createApp"));
assert.ok(!entrypoint.includes("app.get("));
assert.ok(!entrypoint.includes("axios.get("));

const manifest = JSON.parse(read(".vulns"));
const chain = manifest.chained_attacks[0];
assert.equal(chain.chain_id, "chain-01");
assert.equal(chain.impact, "lateral_movement");
assert.equal(chain.components.length, 3);
assert.equal(chain.components[0].method, "getConfig");
assert.equal(chain.components[1].method, "fetchPreview");
assert.equal(chain.components[2].method, "adminSearch");

assert.ok(read("src/controllers/DebugController.ts").includes("CHAIN LINK 1 (chain-01)"));
assert.ok(read("src/services/PreviewService.ts").includes("CHAIN LINK 2 (chain-01)"));
assert.ok(read("src/services/InternalSearchService.ts").includes("CHAIN LINK 3 (chain-01)"));
assert.ok(read("public/js/app.js").includes("VULNERABILITY A03"));

console.log("app-11 contract checks passed");
