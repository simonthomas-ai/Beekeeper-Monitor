'use strict';
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.BeekeeperBackupContract = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  const MAX_BACKUP_BYTES = 30 * 1024 * 1024;
  const MAX_OBSERVATIONS = 10000;
  const MAX_PHOTO_BYTES = 8 * 1024 * 1024;
  const MAX_PHOTO_BASE64_LENGTH = Math.ceil(MAX_PHOTO_BYTES / 3) * 4;
  const TYPES = new Set([
    'Asiatische Hornisse', 'Varroa', 'Drohnenbrut',
    'Pollen', 'Schwarm', 'Königin'
  ]);
  const IMAGE_TYPES = new Set([
    'image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif',
    'image/avif', 'image/heic', 'image/heif', 'image/bmp', 'image/tiff'
  ]);
  const DATA_URL = /^data:(image\/(?:png|jpeg|jpg|webp|gif|avif|heic|heif|bmp|tiff));base64,([A-Za-z0-9+/]+={0,2})$/i;

  function isSupportedImageType(value) {
    return typeof value === 'string' && IMAGE_TYPES.has(value.toLowerCase());
  }

  function validObservation(item) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) return false;
    if (typeof item.id !== 'string' || item.id.length < 1 || item.id.length > 100 || !/^[-a-zA-Z0-9]+$/.test(item.id)) return false;
    if (typeof item.at !== 'string' || item.at.length > 64 || !Number.isFinite(Date.parse(item.at))) return false;
    if (!TYPES.has(item.type) || typeof item.note !== 'string' || !item.note.trim() || item.note.length > 2000) return false;

    if (item.photo !== undefined) {
      const photo = item.photo;
      if (!photo || typeof photo !== 'object' || Array.isArray(photo)) return false;
      if (typeof photo.name !== 'string' || !photo.name || photo.name.length > 255) return false;
      if (!isSupportedImageType(photo.type)) return false;
      if (typeof photo.content !== 'string' || photo.content.length > MAX_PHOTO_BASE64_LENGTH + 32) return false;
      const match = DATA_URL.exec(photo.content);
      if (!match || match[1].toLowerCase() !== photo.type.toLowerCase() || match[2].length % 4 !== 0) return false;
      const base64 = match[2];
      const padding = base64.endsWith('==') ? 2 : base64.endsWith('=') ? 1 : 0;
      const decodedBytes = (base64.length / 4) * 3 - padding;
      if (decodedBytes > MAX_PHOTO_BYTES) return false;
    }

    if (item.location !== undefined) {
      const location = item.location;
      if (!location || typeof location !== 'object' || Array.isArray(location)) return false;
      if (!Number.isFinite(location.latitude) || !Number.isFinite(location.longitude)) return false;
      if (Math.abs(location.latitude) > 90 || Math.abs(location.longitude) > 180) return false;
      if (location.accuracyMeters !== undefined &&
          (!Number.isFinite(location.accuracyMeters) || location.accuracyMeters < 0 || location.accuracyMeters > 100000)) return false;
    }
    return true;
  }

  function parseBackupText(text) {
    if (typeof text !== 'string' || new TextEncoder().encode(text).byteLength > MAX_BACKUP_BYTES) {
      throw new Error('Die Sicherung überschreitet 30 MB oder ist ungültig.');
    }
    let backup;
    try {
      backup = JSON.parse(text);
    } catch {
      throw new Error('Die Sicherungsdatei enthält kein gültiges JSON.');
    }
    if (!backup || typeof backup !== 'object' || backup.format !== 'beekeeper-monitor-v2' ||
        !Array.isArray(backup.observations) || backup.observations.length > MAX_OBSERVATIONS) {
      throw new Error('Ungültiges Sicherungsformat oder zu viele Beobachtungen.');
    }

    const ids = new Set();
    for (const item of backup.observations) {
      if (!validObservation(item)) throw new Error('Die Sicherung enthält eine ungültige Beobachtung oder ein nicht unterstütztes Bildformat.');
      if (ids.has(item.id)) throw new Error('Die Sicherung enthält doppelte Beobachtungs-IDs.');
      ids.add(item.id);
    }
    return backup.observations;
  }

  return Object.freeze({
    MAX_BACKUP_BYTES,
    MAX_OBSERVATIONS,
    MAX_PHOTO_BYTES,
    isSupportedImageType,
    validObservation,
    parseBackupText
  });
});
