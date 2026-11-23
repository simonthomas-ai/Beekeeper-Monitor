'use strict';
// User-initiated preview and single-frame handoff to the local observation form.
(() => {
  const video = document.getElementById('live-camera');
  const status = document.getElementById('live-media-status');
  const startCamera = document.getElementById('start-camera');
  const startMic = document.getElementById('start-mic');
  const stop = document.getElementById('stop-media');
  const captureShadow = document.getElementById('capture-shadow-frame');
  const shadowStatus = document.getElementById('camera-shadow-status');
  const photoInput = document.getElementById('photo');
  const observationType = document.getElementById('observation-type');
  const observationNote = document.getElementById('observation-note');
  const level = document.getElementById('mic-level');
  let cameraStream = null, micStream = null, context = null, analyser = null, raf = 0;
  const setStatus = message => { status.textContent = message; };
  const secure = () => window.isSecureContext && !!navigator.mediaDevices?.getUserMedia;
  function stopCamera() {
    if (cameraStream) cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
    video.srcObject = null;
    captureShadow.disabled = true;
  }
  function updateCaptureAvailability() {
    captureShadow.disabled = !cameraStream || video.readyState < 2 ||
      video.videoWidth === 0 || video.videoHeight === 0;
  }
  function captureFrameBlob(canvas) {
    return new Promise((resolve, reject) => {
      canvas.toBlob(blob => blob ? resolve(blob) : reject(Error('Kamerabild konnte nicht erzeugt werden.')), 'image/jpeg', 0.88);
    });
  }
  async function captureShadowFrame() {
    if (!cameraStream || video.readyState < 2 || !video.videoWidth || !video.videoHeight) {
      throw Error('Kamera ist noch nicht bereit.');
    }
    const scale = Math.min(1, 1280 / video.videoWidth, 720 / video.videoHeight);
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
    canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
    const context = canvas.getContext('2d', {alpha: false});
    if (!context) throw Error('Lokale Bildverarbeitung ist nicht verfügbar.');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await captureFrameBlob(canvas);
    if (blob.size === 0 || blob.size > window.BeekeeperBackupContract.MAX_PHOTO_BYTES) {
      throw Error('Das Kamerabild ist leer oder größer als 8 MB.');
    }
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    const file = new File([blob], `camera-shadow-${stamp}.jpg`, {type: 'image/jpeg', lastModified: Date.now()});
    const transfer = new DataTransfer();
    transfer.items.add(file);
    photoInput.files = transfer.files;
    observationType.value = 'Kamera-Shadow-Test (nicht bestimmt)';
    if (!observationNote.value.trim()) {
      observationNote.value = 'Manuelles Kamera-Shadow-Einzelbild; Art nicht bestimmt, keine KI-Auswertung.';
    }
    shadowStatus.textContent = 'Einzelbild bereit. Ergänze deine Notiz und speichere die Beobachtung ausdrücklich, um es lokal abzulegen.';
  }
  video.addEventListener('loadedmetadata', updateCaptureAvailability);
  video.addEventListener('playing', updateCaptureAvailability);
  captureShadow.addEventListener('click', async () => {
    captureShadow.disabled = true;
    shadowStatus.textContent = 'Erzeuge ein einzelnes Kamerabild …';
    try {
      await captureShadowFrame();
    } catch (err) {
      shadowStatus.textContent = 'Kein Bild übernommen: ' + err.message;
    } finally {
      updateCaptureAvailability();
    }
  });
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
      updateCaptureAvailability();
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
  window.BeekeeperLiveMedia = Object.freeze({ready:true});
})();
