# Automated test operation

The workflow `.github/workflows/gesamttest.yml` runs automatically on every push to `main`, and can also be launched manually.

It checks static PWA code, browser tests, European taxonomy against an external API, training-data inventory, strict train/validation/test annotation presence, and the public site.

**Expected until real datasets arrive:** the training-data validation step fails. This is a legitimate blocker and must not be described as a trained or validated AI model.

A passing taxonomic name lookup is not evidence of European occurrence, image licensing, or model performance.

To inspect the latest run: https://github.com/simonthomas-ai/Beekeeper-Monitor/actions/workflows/gesamttest.yml
