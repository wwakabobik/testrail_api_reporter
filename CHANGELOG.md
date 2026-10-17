# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.1] - 2026-10-17

### Fixed

- `upload_image` now sends a browser-like `User-Agent` header.
  `freeimage.host` (Chevereto, behind Cloudflare) started rejecting
  every upload from this project's CI with a generic
  `400 {"error":{"message":"Internal upload error","code":111}}`,
  regardless of the uploaded content or the API key — raw diagnostics
  captured on CI ruled out duplicate-content and rate-limit theories
  first. The error isn't one of Chevereto's documented API codes
  (100 invalid key, 110 invalid version, 120 invalid action, 130 empty
  source), which points to a WAF/bot-detection rule instead; the
  default `python-requests` user agent is a common target for that
  kind of rule on Cloudflare-fronted sites.
- `test_upload_image_live_success` also uploads a freshly generated,
  randomly-colored image instead of the static fixture file, so it no
  longer depends on content that's been re-uploaded, byte-for-byte, on
  every CI run for a long time.

## [1.6.0] - 2026-10-17

### Added

- Statement and branch test coverage raised to 99% (from ~33%), adding
  tests for every previously untested engine and publisher: `at_coverage_reporter`,
  `case_backup`, `confluence_sender`, `email_sender`, `gdrive_uploader`,
  `results_reporter`, `slack_sender`, plus the untested
  `PlotlyReporter.draw_history_state_chart`/`draw_history_type_chart`
  methods and a few remaining branch gaps in `utils`.
- `pyproject.toml` now carries real packaging metadata (`[project]` /
  `[build-system]`, setuptools, dynamic version read from
  `testrail_api_reporter.__version__`) so the package can be built with
  `python -m build` and checked with `twine check`.

### Changed

- `tests.yml`/`master_tests.yml` now measure branch coverage too
  (`--cov-branch`), and the enforced floor in `tests.yml` is raised from
  95% to 99% statement+branch combined, matching what is actually
  achievable without touching production code (see below).

### Known gaps (not fixed, by design)

The remaining 1% is dead/unreachable code uncovered by any test, confirmed
via direct analysis rather than left unexamined:

- `at_coverage_reporter.__get_all_sections`/`__get_all_cases` and
  `results_reporter.__ensure_automation_section`/`__get_all_auto_cases`:
  a pagination `elif response["_links"]["next"] is not None` branch whose
  `False` side can never be taken once the loop re-enters (the loop only
  re-enters when that exact value was non-`None`).
- `results_reporter.__search_for_run_by_name`: `response` is reset to
  `None` at the top of every loop iteration, so pagination (a second
  page) always crashes with `TypeError` before ever reaching the second
  page's own code — covered by a test documenting the crash, not a
  successful pagination.

Fixing these would mean changing production code, which is out of scope
for a test-only coverage pass.

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
