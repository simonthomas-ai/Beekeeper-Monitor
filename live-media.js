'use strict';
// User-initiated live media preview only. No recognition, recording or upload.
(() => {
  const video = document.getElementById('live-camera');
  const status = document.getElementById('live-media-status');
  const startCamera = document.getElementById('start-camera');
  const startMic = document.getElementById('start-mic');
  const stop = document.getElementById('stop-media');
  const level = document.getElementById('mic-level');
  const modelSelect = document.getElementById('camera-model');
  const modelStatus = document.getElementById('camera-model-status');
  const modelNames = Object.freeze({
    none: 'Kein KI-Modell',
    hornet3000: 'Hornet3000 (Hornissenerkennung)',
    'varroa-board': 'VarroDetector (Bodeneinlage)',
    'varroa-bee': 'Gratheon (Milben auf Bienen)'
  });
  function updateModelStatus() {
    const name = Object.prototype.hasOwnProperty.call(modelNames, modelSelect.value)
      ? modelNames[modelSelect.value] : modelNames.none;
    modelStatus.textContent = modelSelect.value === 'none'
      ? 'Aktiv: kein KI-Modell. Kameravorschau ist möglich.'
      : 'Ausgewählt: ' + name + '. Status: NICHT AKTIV – kein Browsermodell geladen, keine Erkennung.';
  }
  modelSelect.addEventListener('change', updateModelStatus);
  updateModelStatus();

  let cameraStream = null, micStream = null, context = null, analyser = null, raf = 0;
  const setStatus = message => { status.textContent = message; };
  const secure = () => window.isSecureContext && !!navigator.mediaDevices?.getUserMedia;
  function stopCamera() {
    if (cameraStream) cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
    video.srcObject = null;
  }
  async function stopMic() {
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    if (micStream) micStream.getTracks().forEach(track => track.stop());
    micStream = null;
    if (context) { await context.close().catch(() => {}); context = null; }
    analyser = null;
    level.value = 0;
  }
  async function stopAll() {
    stopCamera();
    await stopMic();
    setStatus('Kamera und Mikrofon ausgeschaltet.');
  }
  startCamera.addEventListener('click', async () => {
    if (!secure()) { setStatus('Kamera benötigt HTTPS und Browserfreigabe.'); return; }
    startCamera.disabled = true;
    try {
      stopCamera();
      const stream = await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});
      cameraStream = stream;
      video.srcObject = stream;
      await video.play();
      setStatus('Kamera-Vorschau aktiv. Keine KI-Auswertung, keine Übertragung.');
    } catch (err) {
      stopCamera();
      setStatus('Kamera nicht verfügbar oder Freigabe abgelehnt (' + err.name + ').');
    } finally { startCamera.disabled = false; }
  });
  startMic.addEventListener('click', async () => {
    if (!secure()) { setStatus('Mikrofon benötigt HTTPS und Browserfreigabe.'); return; }
    startMic.disabled = true;
    try {
      await stopMic();
      const stream = await navigator.mediaDevices.getUserMedia({audio:true,video:false});
      micStream = stream;
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) throw Error('AudioContextUnavailable');
      context = new AudioContextClass();
      const source = context.createMediaStreamSource(stream);
      analyser = context.createAnalyser();
      analyser.fftSize = 1024;
      source.connect(analyser); // Intentionally NOT connected to speakers or network.
      const samples = new Uint8Array(analyser.fftSize);
      function update() {
        if (!analyser) return;
        analyser.getByteTimeDomainData(samples);
        let sum = 0;
        for (const sample of samples) { const v = (sample - 128) / 128; sum += v*v; }
        level.value = Math.min(100, Math.round(Math.sqrt(sum / samples.length) * 250));
        raf = requestAnimationFrame(update);
      }
      update();
      setStatus('Mikrofon-Pegel aktiv. Keine Aufnahme, Speicherung oder KI-Auswertung.');
    } catch (err) {
      await stopMic();
      setStatus('Mikrofon nicht verfügbar oder Freigabe abgelehnt (' + (err.name || 'Fehler') + ').');
    } finally { startMic.disabled = false; }
  });
  stop.addEventListener('click', stopAll);
  window.addEventListener('pagehide', () => { stopCamera(); void stopMic(); });
})();
