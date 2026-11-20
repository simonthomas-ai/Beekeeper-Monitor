# Autonomous publishing and operational checks

## Automatic
- Push to main triggers `.github/workflows/pages.yml` to validate and deploy the static PWA.
- `.github/workflows/browser.yml` runs Chromium integration checks.
- `.github/workflows/site-health.yml` checks the public URL and five assets daily.
- `.github/workflows/sources.yml` audits the research source catalog weekly.
- `.github/workflows/training-data.yml` deliberately fails until actual labeled images exist.

## One-time GitHub setting
Under repository Settings > Pages choose **Build and deployment > Source: GitHub Actions**.
The repository workflow cannot guarantee this setting is enabled. Check Actions for deployment errors.

## Expected public URL
https://simonthomas-ai.github.io/Beekeeper-Monitor/

## Boundaries
This deployment serves a **manual observation PWA**, not trained AI.
GitHub Actions scheduled workflows are best-effort, not an always-on computer.
iOS camera, geolocation, offline restart, and backup import still need physical-device acceptance.
No automatic SMS, server push, triangulation, 24-language support, model inference, or validated 99% accuracy is implemented.

## Threshold alert (local, opt-in)
The PWA can warn about `vespa_velutina` candidates from the local station receiver (`camera_detection` / `acoustic_event`) at or above a configurable confidence (default 100%, minimum 50%). It is off by default and only works while the page is open via `http://127.0.0.1:8765/` and connected with the receiver key; there is no background service, so a closed tab means no warning. Warnings use an in-page banner, a tone and, if permitted, a system notification. Each event alerts once, events older than 15 minutes are ignored and a 5-minute cooldown limits bursts. Every warning is labelled an unconfirmed suspicion from an unvalidated model, not a species identification. Remote or SMS delivery needs a separately reviewed, privacy-checked service and is not part of this.
