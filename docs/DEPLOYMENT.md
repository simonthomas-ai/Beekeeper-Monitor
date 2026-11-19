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
No automatic SMS, push, triangulation, 24-language support, model inference, or validated 99% accuracy is implemented.
