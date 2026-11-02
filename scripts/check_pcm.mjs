import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
let Processor;
const messages = [];
vm.runInNewContext(await readFile('bolparchi/web/pcm-worklet.js', 'utf8'), {
  AudioWorkletProcessor: class { constructor() { this.port = { postMessage: message => messages.push(message) }; } },
  registerProcessor: (name, implementation) => { Processor = implementation; }, Int16Array, Math,
});
const processor = new Processor();
const block = new Float32Array(128); block.set([-2, -1, -.5, 0, .5, 1, 2]);
for (let index = 0; index < 3750; index++) processor.process([[block]]);
assert.equal(messages.length, 1);
assert.equal(messages[0].samples.length, 480000);
assert.deepEqual([...messages[0].samples.slice(0, 7)], [-32768, -32768, -16384, 0, 16384, 32767, 32767]);
assert.equal(processor.process([[block]]), false);
processor.port.onmessage({ data: 'stop' });
assert.equal(messages.length, 1);
const { pcmWav } = await import(pathToFileURL(`${process.cwd()}/bolparchi/web/recorder.js`));
const data = Buffer.from(await pcmWav(messages[0].samples).arrayBuffer());
assert.equal(data.length, 960044); assert.equal(data.readUInt32LE(4), 960036); assert.equal(data.readUInt32LE(40), 960000);
assert.equal(data.readInt16LE(44), -32768); assert.equal(data.readInt16LE(52), 16384);
assert.throws(() => pcmWav(new Int16Array(480001)));
assert.throws(() => pcmWav(new Int16Array()));
console.log('PASS: exact 30-second sample bound, clipping/sign/little-endian PCM, single completion and oversized/empty encoder rejection.');
