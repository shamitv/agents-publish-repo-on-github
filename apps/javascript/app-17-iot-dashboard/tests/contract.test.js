const assert = require('assert');
const fs = require('fs');
const path = require('path');

const appRoot = path.resolve(__dirname, '..');
const read = (relativePath) => fs.readFileSync(path.join(appRoot, relativePath), 'utf8');
const exists = (relativePath) => fs.existsSync(path.join(appRoot, relativePath));

assert.ok(exists('src/controllers/DeviceController.js'));
assert.ok(exists('src/services/DeviceService.js'));
assert.ok(exists('src/services/RefreshService.js'));
assert.ok(exists('src/services/TelemetryService.js'));
assert.ok(exists('src/repositories/DeviceRepository.js'));
assert.ok(exists('src/db/InMemoryStore.js'));
assert.ok(exists('src/cache/SessionCache.js'));
assert.ok(exists('src/mq/EventProducer.js'));
assert.ok(exists('src/search/DeviceSearchClient.js'));

const entrypoint = read('src/index.js');
assert.ok(entrypoint.includes('createApp'));
assert.ok(!entrypoint.includes('app.post('));
assert.ok(!entrypoint.includes('axios.get('));

const manifest = JSON.parse(read('.vulns'));
const chain = manifest.chained_attacks[0];
assert.equal(chain.chain_id, 'chain-01');
assert.equal(chain.impact, 'lateral_movement');
assert.equal(chain.components.length, 3);
assert.equal(chain.components[0].method, 'commandError');
assert.equal(chain.components[1].method, 'refreshStatus');
assert.equal(chain.components[2].method, 'internalTelemetry');

assert.ok(read('src/services/DeviceService.js').includes('CHAIN LINK 1 (chain-01)'));
assert.ok(read('src/services/RefreshService.js').includes('CHAIN LINK 2 (chain-01)'));
assert.ok(read('src/services/TelemetryService.js').includes('CHAIN LINK 3 (chain-01)'));

const { createApp } = require('../src/app');
assert.ok(createApp());

console.log('app-17 contract checks passed');
