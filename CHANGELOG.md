# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-10-17

### Changed

- Bumped all runtime dependencies to their latest available versions
  (`atlassian-python-api`, `google-api-python-client`, `google-auth-httplib2`,
  `google-auth-oauthlib`, `httplib2`, `kaleido`, `oauth2client`, `plotly`,
  `psutil`, `requests`, `testrail-api`, `xmltodict`).
- Added Python 3.14 and 3.15 to the CI test and linter matrices.
- Regenerated the `PlotlyReporter` expected image fixtures to match the
  rendering output of the bumped `kaleido`/`plotly` versions.

### Removed

- Dropped Python 3.9 from the CI matrix: it reached end-of-life in
  October 2025, and the latest `google-api-python-client`,
  `google-auth-httplib2`, `google-auth-oauthlib` and `requests` releases
  already require Python 3.10+.

### Added

- A Chrome install step in the test workflows, required by `kaleido>=1.0`
  to render chart images.
