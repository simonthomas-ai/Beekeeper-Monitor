# Model acceptance gate

A model is **not integrated** until all gates pass:

1. Source URL, author, version, license and redistribution rights documented.
2. Actual model weights available with immutable checksum.
3. Real training and independent holdout data documented; no invented labels.
4. Classes mapped explicitly to the intended task (drone != drone brood).
5. Reproducible preprocessing and inference implemented.
6. Precision, recall, confusion matrix, false alarms, and latency measured on independent data.
7. Browser/mobile compatibility tested on iPhone and Android; no desktop-only executable disguised as PWA.
8. Offline availability and model download size verified.
9. Privacy and permissions reviewed.
10. Results presented with model version, confidence, and uncertainty.

The current target is **one experimental seven-class insect detector**, not six independently validated models. No 99% accuracy claim before all gates pass.

## Known blockers
- VespAI access/non-commercial licensing requires review.
- Queen model training repository states model weights are not committed.
- Pollen-bearing bee detection is not equivalent to pollen species identification.
- Drone detection is not drone-brood detection.
- Beehive audio does not automatically establish swarm recognition.
- Free cloud compute is quota-limited, not guaranteed 24/7.

## Current status
The ten acceptance criteria above are **not yet satisfied as a complete set**. The project has no approved detector weights or independently validated field accuracy. Passing software CI does not constitute model acceptance.
