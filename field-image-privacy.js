'use strict';
(() => {
  const MAX_SOURCE_BYTES = 8 * 1024 * 1024;
  const MAX_IMAGE_PIXELS = 16_000_000;
  const MAX_EXPORT_IMAGE_BYTES = 40 * 1024 * 1024;
  const MAX_TOTAL_EXPORT_BYTES = 96 * 1024 * 1024;
  const PNG_SIGNATURE = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]);
  const JPEG_SOF = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]);

  function fail(message) {
    throw new Error(message);
  }

  function ascii(bytes, start, length) {
    return String.fromCharCode(...bytes.subarray(start, start + length));
  }

  function readU32BE(bytes, offset) {
    return ((bytes[offset] * 0x1000000) +
      (bytes[offset + 1] << 16) +
      (bytes[offset + 2] << 8) +
      bytes[offset + 3]) >>> 0;
  }

  function readU32LE(bytes, offset) {
    return (bytes[offset] |
      (bytes[offset + 1] << 8) |
      (bytes[offset + 2] << 16) |
      (bytes[offset + 3] << 24)) >>> 0;
  }

  function readU24LE(bytes, offset) {
    return bytes[offset] | (bytes[offset + 1] << 8) | (bytes[offset + 2] << 16);
  }

  function checkDimensions(width, height) {
    if (!Number.isSafeInteger(width) || !Number.isSafeInteger(height) ||
        width < 1 || height < 1 || width * height > MAX_IMAGE_PIXELS) {
      fail('Bild abgewiesen: Abmessungen fehlen oder überschreiten 16 Megapixel. Bitte lokal eine kleinere, unveränderte Aufnahme auswählen.');
    }
    return {width, height};
  }

  function pngDimensions(bytes) {
    if (bytes.length < 33 || !PNG_SIGNATURE.every((value, index) => bytes[index] === value) ||
        readU32BE(bytes, 8) !== 13 || ascii(bytes, 12, 4) !== 'IHDR') {
      fail('PNG-Bild ist ungültig oder unvollständig.');
    }
    let offset = 8;
    while (offset + 12 <= bytes.length) {
      const size = readU32BE(bytes, offset);
      const type = ascii(bytes, offset + 4, 4);
      if (size > bytes.length - offset - 12) fail('PNG-Bild enthält einen ungültigen Chunk.');
      if (type === 'acTL') fail('Animierte PNG-Bilder werden aus Sicherheits- und Eindeutigkeitsgründen nicht exportiert.');
      offset += size + 12;
      if (type === 'IEND') break;
    }
    return checkDimensions(readU32BE(bytes, 16), readU32BE(bytes, 20));
  }

  function jpegDimensions(bytes) {
    if (bytes.length < 4 || bytes[0] !== 0xff || bytes[1] !== 0xd8) {
      fail('JPEG-Bild ist ungültig oder stimmt nicht mit dem Dateityp überein.');
    }
    let offset = 2;
    while (offset < bytes.length) {
      if (bytes[offset] !== 0xff) fail('JPEG-Bild enthält eine ungültige Markerfolge.');
      while (offset < bytes.length && bytes[offset] === 0xff) offset++;
      if (offset >= bytes.length) break;
      const marker = bytes[offset++];
      if (marker === 0xd9 || marker === 0xda) break;
      if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) continue;
      if (offset + 2 > bytes.length) fail('JPEG-Bild enthält einen unvollständigen Marker.');
      const segmentLength = (bytes[offset] << 8) | bytes[offset + 1];
      if (segmentLength < 2 || segmentLength > bytes.length - offset) {
        fail('JPEG-Bild enthält einen ungültigen Segmentumfang.');
      }
      const payload = offset + 2;
      if (marker === 0xe2 && segmentLength >= 6 && ascii(bytes, payload, 4) === 'MPF\0') {
        fail('Mehrbild-JPEGs werden nicht exportiert; bitte ein einzelnes Bild auswählen.');
      }
      if (JPEG_SOF.has(marker)) {
        if (segmentLength < 7) fail('JPEG-Bild enthält ungültige Abmessungen.');
        const height = (bytes[offset + 3] << 8) | bytes[offset + 4];
        const width = (bytes[offset + 5] << 8) | bytes[offset + 6];
        return checkDimensions(width, height);
      }
      offset += segmentLength;
    }
    fail('JPEG-Abmessungen konnten nicht sicher gelesen werden.');
  }

  function webpDimensions(bytes) {
    if (bytes.length < 30 || ascii(bytes, 0, 4) !== 'RIFF' || ascii(bytes, 8, 4) !== 'WEBP' ||
        readU32LE(bytes, 4) + 8 !== bytes.length) {
      fail('WebP-Bild ist ungültig oder unvollständig.');
    }
    let offset = 12;
    let dimensions = null;
    while (offset + 8 <= bytes.length) {
      const type = ascii(bytes, offset, 4);
      const size = readU32LE(bytes, offset + 4);
      const data = offset + 8;
      if (size > bytes.length - data) fail('WebP-Bild enthält einen ungültigen Chunk.');
      if (type === 'ANIM' || type === 'ANMF') {
        fail('Animierte WebP-Bilder werden aus Sicherheits- und Eindeutigkeitsgründen nicht exportiert.');
      }
      if (type === 'VP8X') {
        if (size < 10) fail('WebP-Erweiterungsheader ist ungültig.');
        if (bytes[data] & 0x02) fail('Animierte WebP-Bilder werden aus Sicherheits- und Eindeutigkeitsgründen nicht exportiert.');
        dimensions = checkDimensions(1 + readU24LE(bytes, data + 4), 1 + readU24LE(bytes, data + 7));
        break;
      }
      if (type === 'VP8 ' && size >= 10 &&
          bytes[data + 3] === 0x9d && bytes[data + 4] === 0x01 && bytes[data + 5] === 0x2a) {
        const width = ((bytes[data + 7] << 8) | bytes[data + 6]) & 0x3fff;
        const height = ((bytes[data + 9] << 8) | bytes[data + 8]) & 0x3fff;
        dimensions = checkDimensions(width, height);
        break;
      }
      if (type === 'VP8L' && size >= 5 && bytes[data] === 0x2f) {
        const b1 = bytes[data + 1], b2 = bytes[data + 2], b3 = bytes[data + 3], b4 = bytes[data + 4];
        const width = 1 + (((b2 & 0x3f) << 8) | b1);
        const height = 1 + (((b4 & 0x0f) << 10) | (b3 << 2) | ((b2 & 0xc0) >> 6));
        dimensions = checkDimensions(width, height);
        break;
      }
      offset = data + size + (size & 1);
    }
    if (!dimensions) fail('WebP-Abmessungen konnten nicht sicher gelesen werden.');
    return dimensions;
  }

  function inspectSource(bytes, type) {
    if (!(bytes instanceof Uint8Array)) bytes = new Uint8Array(bytes);
    if (bytes.length < 1 || bytes.length > MAX_SOURCE_BYTES) {
      fail('Bildgröße außerhalb des erlaubten Bereichs; maximal 8 MB pro Originalbild.');
    }
    if (type === 'image/png') return pngDimensions(bytes);
    if (type === 'image/jpeg') return jpegDimensions(bytes);
    if (type === 'image/webp') return webpDimensions(bytes);
    fail('Nicht unterstütztes Bildformat. Nur JPEG, PNG und WebP sind erlaubt.');
  }

  function crc32Parts(first, second) {
    let crc = 0xffffffff;
    for (const part of [first, second]) {
      for (const byte of part) {
        crc ^= byte;
        for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
      }
    }
    return (crc ^ 0xffffffff) >>> 0;
  }

  function stripPngMetadata(input) {
    if (input.length < 33 || !PNG_SIGNATURE.every((value, index) => input[index] === value)) {
      fail('Der Browser hat kein gültiges PNG erzeugt; Export wird ohne Originalbild-Fallback abgebrochen.');
    }
    const chunks = [input.slice(0, 8)];
    let total = 8;
    let offset = 8;
    let seenHeader = false;
    let seenData = false;
    let dataClosed = false;
    let seenEnd = false;
    const kept = new Set(['IHDR', 'PLTE', 'tRNS', 'IDAT', 'IEND']);
    const critical = new Set(['IHDR', 'PLTE', 'IDAT', 'IEND']);
    while (offset < input.length) {
      if (offset + 12 > input.length) fail('PNG-Metadatenprüfung: unvollständiger Chunk.');
      const size = readU32BE(input, offset);
      const typeBytes = input.subarray(offset + 4, offset + 8);
      const type = ascii(input, offset + 4, 4);
      if (!/^[A-Za-z]{4}$/.test(type) || size > input.length - offset - 12) {
        fail('PNG-Metadatenprüfung: ungültiger Chunk.');
      }
      const data = input.subarray(offset + 8, offset + 8 + size);
      const storedCrc = readU32BE(input, offset + 8 + size);
      if (crc32Parts(typeBytes, data) !== storedCrc) fail('PNG-Metadatenprüfung: CRC-Prüfung fehlgeschlagen.');
      if (!seenHeader) {
        if (type !== 'IHDR' || size !== 13 || offset !== 8) fail('PNG-Metadatenprüfung: IHDR fehlt oder ist ungültig.');
        seenHeader = true;
      } else if (type === 'IHDR') {
        fail('PNG-Metadatenprüfung: doppelter IHDR-Chunk.');
      }
      if (type === 'IDAT') {
        if (dataClosed) fail('PNG-Metadatenprüfung: nicht zusammenhängende Bilddaten.');
        seenData = true;
      } else if (seenData && type !== 'IEND') {
        dataClosed = true;
      }
      if (type === 'PLTE' || type === 'tRNS') {
        if (seenData) fail('PNG-Metadatenprüfung: Farbtabellen stehen an einer ungültigen Position.');
      }
      if ((type.charCodeAt(0) & 0x20) === 0 && !critical.has(type)) {
        fail('PNG-Metadatenprüfung: unbekannter kritischer Chunk.');
      }
      if (kept.has(type)) {
        const chunk = input.slice(offset, offset + size + 12);
        chunks.push(chunk);
        total += chunk.length;
      }
      offset += size + 12;
      if (type === 'IEND') {
        if (size !== 0 || !seenData || offset !== input.length) {
          fail('PNG-Metadatenprüfung: ungültiges Dateiende.');
        }
        seenEnd = true;
        break;
      }
    }
    if (!seenHeader || !seenData || !seenEnd) fail('PNG-Metadatenprüfung: unvollständige PNG-Datei.');
    const output = new Uint8Array(total);
    let cursor = 0;
    for (const chunk of chunks) {
      output.set(chunk, cursor);
      cursor += chunk.length;
    }
    return output;
  }

  async function decodeImage(blob) {
    if (typeof createImageBitmap === 'function') {
      try {
        const bitmap = await createImageBitmap(blob);
        return {
          source: bitmap,
          width: bitmap.width,
          height: bitmap.height,
          dispose: () => bitmap.close()
        };
      } catch {
        // Fall through to the image-element decoder; never fall back to raw bytes.
      }
    }
    const url = URL.createObjectURL(blob);
    const image = new Image();
    image.decoding = 'async';
    try {
      image.src = url;
      if (typeof image.decode === 'function') {
        await image.decode();
      } else {
        await new Promise((resolve, reject) => {
          image.onload = resolve;
          image.onerror = () => reject(new Error('Bild konnte nicht dekodiert werden.'));
        });
      }
      return {
        source: image,
        width: image.naturalWidth,
        height: image.naturalHeight,
        dispose: () => URL.revokeObjectURL(url)
      };
    } catch {
      URL.revokeObjectURL(url);
      fail('Bild konnte im Browser nicht sicher dekodiert werden; Originalbytes werden nicht exportiert.');
    }
  }

  async function sanitizeImageForExport(sourceBytes, sourceType) {
    const bytes = sourceBytes instanceof Uint8Array
      ? sourceBytes
      : new Uint8Array(sourceBytes);
    inspectSource(bytes, sourceType);
    const decoded = await decodeImage(new Blob([bytes], {type:sourceType}));
    const canvas = document.createElement('canvas');
    try {
      const width = decoded.width;
      const height = decoded.height;
      checkDimensions(width, height);
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext('2d');
      if (!context) fail('Lokale Bildbereinigung ist in diesem Browser nicht verfügbar.');
      context.drawImage(decoded.source, 0, 0, width, height);
      const encoded = await new Promise((resolve, reject) => {
        canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error('PNG-Neukodierung fehlgeschlagen.')), 'image/png');
      });
      if (encoded.type !== 'image/png') fail('Der Browser hat kein PNG erzeugt; Export wird abgebrochen.');
      const encodedBytes = new Uint8Array(await encoded.arrayBuffer());
      if (encodedBytes.length > MAX_EXPORT_IMAGE_BYTES) {
        fail('Bereinigtes Bild überschreitet 40 MB. Bitte weniger oder kleinere Bilder in getrennten Exporten verwenden.');
      }
      return stripPngMetadata(encodedBytes);
    } finally {
      canvas.width = 0;
      canvas.height = 0;
      decoded.dispose();
    }
  }

  window.BeeKeeperImagePrivacy = Object.freeze({
    sanitizeImageForExport,
    limits: Object.freeze({
      maxImagePixels: MAX_IMAGE_PIXELS,
      maxExportImageBytes: MAX_EXPORT_IMAGE_BYTES,
      maxTotalExportBytes: MAX_TOTAL_EXPORT_BYTES
    })
  });
})();
