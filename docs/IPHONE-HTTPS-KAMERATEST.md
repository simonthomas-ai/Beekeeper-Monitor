# Privater iPhone-Kameratest über GitHub Codespaces

**Zweck:** HTTPS-Vorschau der aktuellen PWA, ohne GitHub Pages öffentlich freizuschalten.
Dies ist keine Freigabe für einen öffentlichen Betrieb und kein Nachweis der Erkennungsgenauigkeit.

1. Auf dem iPhone mit dem GitHub-Konto anmelden und das Repository öffnen:
   https://github.com/simonthomas-ai/Beekeeper-Monitor
2. **Code → Codespaces → Create codespace on main** wählen. Ein Codespace benötigt eine verfügbare GitHub-Codespaces-Berechtigung und kann Kosten verursachen; Quoten beachten.
3. Nach dem Start den Tab **Ports** öffnen. Port **8000** wird automatisch weitergeleitet. Port-Sichtbarkeit **Private** belassen. Die angezeigte weitergeleitete HTTPS-Adresse im Safari-Browser öffnen. Die konkrete Adresse wird von GitHub erzeugt und kann hier nicht vorab angegeben werden.
4. **Kamera einschalten** → im Feld **KI-Modell** Hornet3000 wählen.
5. Für die experimentelle KI muss die exakt passende ONNX-Datei auf dem iPhone vorliegen. Erwartet werden **44.737.849 Bytes** und SHA-256 `1df95cedd08426dc218f8aa9e02667e068c0bda218c29a44032638fab005276f`. Das Original liegt upstream unter https://github.com/vespCV/hornet3000/blob/78f51980ee99e45748e78e54dd1312cff846a5ac/yolov8sModel/best.onnx . Nutzungsrechte für Gewichte gesondert prüfen. Kein automatischer Download oder Redistribution.
6. ONNX-Datei auswählen → **Experimentelle Kamera-KI starten**. Die ONNX-Laufzeit wird online von jsDelivr bezogen; Kamerabilder bleiben im Browser. Anzeige: **unbestätigte Kandidaten**, keine automatische Alarmierung.
7. Mit **KI stoppen** beenden und nach dem Test den Codespace stoppen, um Ressourcen/Kosten zu begrenzen.

**Einschränkungen:** Die Vorschau ist nur über die von GitHub erzeugte HTTPS-Portadresse erreichbar. Ohne GitHub-Anmeldung/Codespace oder bei nicht erreichbarem CDN funktioniert die experimentelle KI nicht. Codespaces und iOS-Safari wurden noch nicht praktisch auf einem echten iPhone geprüft. Das Modell kann falsch-positive und falsch-negative Kandidaten erzeugen. Varroa-Modelle sind noch nicht browserfähig.

**Fehlersuche:** Wenn Port 8000 nicht angezeigt wird, im Codespaces-Terminal `python3 -m http.server 8000 --bind 0.0.0.0` starten. Bei Kamera-Problemen sicherstellen, dass die Vorschau in Safari über **HTTPS** geöffnet und die Kameraberechtigung erteilt wurde.
