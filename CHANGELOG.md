# Changelog

All notable changes to MatMat will be documented in this file.

## [0.9.1-beta] - ?

### Added
- Restore data packages missing in previous version
- Update GitHub actions to work on 'main' branch
- Remove OS-compatibility GitHub actions

## [0.9.0-beta] - 2026-06-20

### Added
- First public open-source release of MatMat.
- Python package structure based on `pyproject.toml`.
- Public documentation in `README.md`.
- Citation metadata through `CITATION.cff`.
- Open-source licensing under CeCILL.
- GitHub repository and release workflow.

### Included packages
- `core`: core Environmentally-Extended Input-Output (EEIO) modelling framework.
- `workflows`: high-level workflows for preparing, running, and analysing MatMat case studies, including:
  - `adapters`: conversion and formatting of external datasets into MatMat-compatible inputs;
  - `pipelines`: preparation of case-study-specific input data;
  - `engines`: direct application of the core modelling framework;
  - `analyses`: framework for post-processing, result formatting, and figure generation. Public analysis workflows will be progressively expanded in future releases.
- `utils`: shared utility functions supporting data and file management, logging, error handling, and constant definitions.

### Excluded from this release
- Legacy adapters developed for historical data formats that are no longer maintained.
- Adapters currently under development and not yet considered stable.
- The analyses workflow package, which is still being consolidated and documented.
- Internal ADEME-specific scripts and utilities.

### Notes
- This release provides the first public open-source version of MatMat and is intended to support transparency, reproducibility, review, and reuse of the research conducted during its development.
- A consolidated stable release (v1.0.0) is planned following additional documentation, testing, validation, and packaging improvements.

## [1.0.0] - Unreleased

### Planned
- Stabilise the public API.
- Complete user documentation.
- Add developer documentation.
- Consolidate and document missing public workflows, including selected adapters and analyses workflows.
- Maintain continuous integration and automated testing.
- Improve packaging and distribution.
- Improve computational performance, memory usage, and data processing efficiency.
- Add examples and tutorials.
