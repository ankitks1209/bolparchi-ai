// The audio thread enforces the sample bound even if the UI timer is delayed.
class BoundedPCM extends AudioWorkletProcessor {
  constructor() {
    super();
    this.samples = new Int16Array(16000 * 30); this.count = 0; this.done = false;
    this.port.onmessage = event => { if (event.data === 'stop') this.finish(); };
  }
  finish() {
    if (this.done) return;
    this.done = true;
    const samples = this.samples.slice(0, this.count); this.samples = null;
    this.port.postMessage({ type: 'complete', samples }, [samples.buffer]);
  }
  process(inputs) {
    if (this.done) return false;
    const input = inputs[0]?.[0];
    if (input) {
      const length = Math.min(input.length, this.samples.length - this.count);
      for (let index = 0; index < length; index++) {
        const value = Math.max(-1, Math.min(1, input[index]));
        this.samples[this.count++] = Math.round(value * (value < 0 ? 32768 : 32767));
      }
      if (this.count === this.samples.length) this.finish();
    }
    return !this.done;
  }
}
registerProcessor('bolparchi-pcm', BoundedPCM);
