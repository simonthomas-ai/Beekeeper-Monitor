# VespaGuard ecosystem — upstream integration registry

This registry is a **discovery list**, not a claim of compatibility, license clearance, installation, model accuracy, or successful integration. Do not copy upstream source, model weights, datasets, photographs, or binaries into this repository until each artifact's license, provenance, attribution, and compatibility have been reviewed. GitHub public visibility is not a license.

| Upstream | Potential role | License status / restrictions | Next action |
| --- | --- | --- | --- |
| https://github.com/vespCV/hornet3000 | Raspberry Pi YOLO hornet detection | GitHub indicates GPL-3.0; archived; verify license for code, models and dataset separately | Review code/model/data licenses and dependency tree |
| https://github.com/andrw3000/vespai | Distinguish Vespa velutina vs Vespa crabro | Not yet verified | Inspect LICENSE, weights and image provenance |
| https://github.com/jeroen-kanters/Hornet_Trap | Smart vision trap, ESP32 | Publisher states GNU GPL; exact version and components need verification | Review firmware and safety constraints |
| https://github.com/PauMonterosa/vespa-velutina-tracker | Tracking with camera, ESP32 and Raspberry Pi | Not yet verified | Review code license and avoid automated capture |
| https://github.com/philippkueng/auditive_detection_of_asian_hornets | Acoustic classification | Not yet verified | Review code, training sound rights and test data |
| https://github.com/mbron64/buzzhive-open | Audio and hive sensors | Publisher states Apache-2.0; inspect individual assets | Review hardware/firmware interfaces |
| https://github.com/MacNite/HiveHub | Multi-hive telemetry | Publisher states MIT | Review MQTT/API integration |
| https://github.com/jodivaso/varrodetector | Varroa counting | Not yet verified | Review model weights, image dataset and license |
| https://github.com/WataNekko/aiot-beehive | Bee counting and wasp detection | Not yet verified | Review modules and licenses |
| https://github.com/gitDew/waspinator | Hornet vs native hornet detection | Not yet verified; trapping functionality present | Only consider detection; do not enable trapping |
| https://github.com/divednakumari-lab/beehive-monitor | Low-cost ESP32 temperature/humidity | Publisher states MIT | Review hardware interface |

## Proposed modular architecture

1. **Detection:** interchangeable camera inference adapters, offline-first; no claimed accuracy without a held-out real-world evaluation.
2. **Hive health:** optional temperature, humidity, weight, audio, and Varroa modules with clearly distinguished sensor evidence.
3. **Notifications:** opt-in alerts, local queues, and optional server-side integrations; never promise SMS without a provider and connectivity.
4. **Review:** manual species verification, false-positive analysis, provenance and license audit; training approval remains closed by default.
5. **Hardware:** Raspberry Pi and ESP32 adapters with simulated-device tests clearly labeled as simulation.
6. **PWA:** accessible, multilingual, phone-first controls; no automatic third-party code execution.

## Integration gates

- Record upstream commit and exact SPDX license per copied file, dataset and model.
- Check GPL/AGPL reciprocal obligations, model licenses, trademarks, attribution, and third-party dependencies.
- Run code in isolation; never execute untrusted installation scripts automatically.
- Preserve original attribution and license notices.
- Add tests and measured performance before enabling a feature.
- Never automatically activate mechanical traps or claim a device is safe.
- Never mix synthetic data into the held-out real-image evaluation set.

**Current status:** discovery only; no upstream cloned, merged, installed, trained or approved by this document.
