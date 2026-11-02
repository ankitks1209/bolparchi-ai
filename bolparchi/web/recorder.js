export function pcmWav(samples) {
  if (!samples.length || samples.length > 480000) throw new Error('empty_recording');
  const buffer = new ArrayBuffer(44 + samples.length * 2), view = new DataView(buffer);
  const text = (offset, value) => [...value].forEach((character, index) => view.setUint8(offset + index, character.charCodeAt(0)));
  text(0, 'RIFF'); view.setUint32(4, buffer.byteLength - 8, true); text(8, 'WAVE'); text(12, 'fmt ');
  view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
  view.setUint32(24, 16000, true); view.setUint32(28, 32000, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true);
  text(36, 'data'); view.setUint32(40, samples.length * 2, true);
  samples.forEach((sample, index) => view.setInt16(44 + index * 2, sample, true));
  return new Blob([buffer], { type: 'audio/wav' });
}

export class Recorder {
  constructor({ onState, onComplete, onError }) { Object.assign(this, { onState, onComplete, onError }); this.session = null; }
  release(session) {
    clearInterval(session.timer); clearTimeout(session.limit);
    session.stream?.getTracks().forEach(track => track.stop());
    session.source?.disconnect();
    if (session.node) { session.node.port.onmessage = null; session.node.port.close(); session.node.disconnect(); }
    session.context?.close().catch(() => {});
    session.stream = null;
  }
  cancel() {
    const session = this.session; this.session = null;
    if (session) this.release(session);
    this.onState('idle', 0);
  }
  stop() {
    if (!this.session?.node || this.session.stopping) return;
    this.session.stopping = true; this.onState('finishing', 0);
    this.session.node.port.postMessage('stop');
  }
  async start() {
    if (this.session) return;
    const session = {}; this.session = session; this.onState('permission', 0);
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode) throw new Error('unsupported');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true }, video: false });
      if (this.session !== session) { stream.getTracks().forEach(track => track.stop()); return; }
      session.stream = stream;
      session.context = new AudioContext({ sampleRate: 16000 });
      if (session.context.sampleRate !== 16000) throw new Error('unsupported');
      await session.context.audioWorklet.addModule('/pcm-worklet.js');
      if (this.session !== session) return;
      session.node = new AudioWorkletNode(session.context, 'bolparchi-pcm', { channelCount: 1, channelCountMode: 'explicit', numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1] });
      session.node.port.onmessage = event => {
        if (this.session !== session || event.data.type !== 'complete') return;
        this.session = null; this.release(session); this.onState('idle', 0);
        try { this.onComplete(pcmWav(event.data.samples)); }
        catch { this.onError('No audio was captured. Record again or type your update.'); }
      };
      session.source = session.context.createMediaStreamSource(stream);
      session.source.connect(session.node); session.node.connect(session.context.destination);
      await session.context.resume();
      if (this.session !== session) return;
      const start = performance.now(); this.onState('recording', 0);
      session.timer = setInterval(() => this.onState('recording', Math.min(30, (performance.now() - start) / 1000)), 200);
      session.limit = setTimeout(() => this.stop(), 30000);
      stream.getTracks().forEach(track => { track.onended = () => { if (this.session === session) { this.cancel(); this.onError('The microphone disconnected. Record again or type your update.'); } }; });
    } catch (error) {
      if (this.session !== session) return;
      this.cancel();
      this.onError(error.name === 'NotAllowedError' ? 'Microphone access was denied. Allow it in your browser, or type your update.' : 'Recording is unavailable in this browser. Type your update instead.');
    }
  }
}
