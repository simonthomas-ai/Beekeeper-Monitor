# Upstream license audit — 2026-11-19

Evidence: GitHub Actions run https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/runs/44586224317/artifacts/14559074536, `upstream-source-review.json`. This inventory was produced by isolated Git shallow clones, using `git show HEAD:<license-file>` for license text. **Not legal advice or a grant of permission.** License detection is based on conventional license filenames and may miss declarations elsewhere.

| Repository | Pinned upstream commit | Detected license evidence | Tracked files | Candidate assets* | Gate |
| --- | --- | --- | ---: | ---: | --- |
| vespCV/hornet3000 | `78f51980ee` | LICENSE: GNU GPL v3 | 98 | 65 | Review GPL obligations and assets |
| vespCV/vespcv | `a14b2d3563` | LICENSE: summary describing GPL v3 (not full license text) | 54 | 29 | Check authoritative licensing |
| andrw3000/vespai | `004f3d8930` | LICENSE: repository CC BY-NC-SA 4.0, constituent model code AGPL-3.0, dependencies separately licensed | 234 | 162 | **No blanket permission**; review NC/SA and AGPL, files and models individually |
| jeroen-kanters/Hornet_Trap | `6c01cf6450` | LICENSE: GNU GPL v3 | 87 | 75 | Review GPL and physical device safety |
| PauMonterosa/vespa-velutina-tracker | `c41c5c1dfe` | No conventional LICENSE/COPYING/NOTICE detected | 51 | 10 | No copying until permission established |
| philippkueng/auditive_detection_of_asian_hornets | `36d730173f` | No conventional LICENSE/COPYING/NOTICE detected | 43 | 14 | No copying until permission established |
| mbron64/buzzhive-open | `73cf0d8cfb` | LICENSE: Apache-2.0 | 64 | 31 | Candidate for isolated interface review; retain notices |
| MacNite/HiveHub | `84a82d2eb4` | LICENSE: MIT | 332 | 17 | Candidate for isolated interface review; retain notices |
| jodivaso/varrodetector | `31c2cebd28` | LICENSE: GNU AGPL v3 | 14 | 6 | Review network-service and source-sharing obligations |
| WataNekko/aiot-beehive | `3e9f580809` | LICENSE: GNU GPL v3 | 19 | 0 | Review GPL obligations |
| gitDew/waspinator | `7251be99a6` | LICENSE.txt: GNU AGPL v3 | 56 | 3 | Review AGPL; do not enable trapping |
| divednakumari-lab/beehive-monitor | `2a8799116e` | No conventional LICENSE/COPYING/NOTICE detected | 8 | 0 | No copying until permission established |

*Candidate asset count means filenames matching extensions for model weights, images, audio, archives, CSVs etc. It is **not** a count of usable training samples or approved model files.

## Integration policy

1. **Start with independent adapters** using documented public protocols, without importing third-party source or binary assets. Inspect Apache-2.0 and MIT candidates first; their repo-level license evidence is clearer, but every component still needs checking.
2. GPL-3.0 and AGPL-3.0 code require careful license-compatibility and distribution/network-use assessment before copying or linking. An upstream license file does not automatically license every bundled artifact.
3. VespAI's CC BY-NC-SA 4.0 repository terms include noncommercial and share-alike conditions. The constituent model code is separately described as AGPL-3.0. Do not assume either covers trained weights or photos.
4. Where no license was detected, default to **no permission to redistribute or modify**, unless a separate grant is established.
5. Keep training data, weights, photos, sounds and synthetic renders behind separate provenance and species-validation gates. Do not claim 99% detection performance.
6. No upstream code was copied into VespaGuard and no external project was executed by this audit. All training and deployment approvals remain closed.

## Next technical stage

Implement **original**, license-independent data adapters for sensor telemetry, camera detection results, acoustic event summaries and Varroa count results. Define schemas and contract tests first, then review candidate upstream APIs before adding optional connectors. No automatic trapping.
