# Contributing to the New Zealand Medical-Legal Corpus

Thank you for your interest in contributing to the New Zealand Medical-Legal Corpus! This project is part of the `legal-nz` family, aiming to provide high-quality, open legal data for New Zealand.

## How to Contribute

We welcome contributions in the following areas:
- Reporting bugs or data parsing errors
- Adding support for new tribunals or case sources
- Improving ingestion performance or validation schemas
- Enhancing documentation

## Shared Library Architecture

This repository is designed to be **data-centric and lightweight**. 
- Heavy processing, NLP, and scraping logic must reside in the shared [`nlp-policy-nz`](https://github.com/edithatogo/nlp-policy-nz) library.
- This repository houses wrappers, configurations (`config/`), and automated workflow actions (`.github/workflows/`).

If you need to change how text is cleaned or how metadata is extracted, please submit a pull request to the `nlp-policy-nz` repository instead.

## Development Setup

We use `pixi` for environment management and local task execution.

1. Install `pixi` on your machine.
2. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/edithatogo/corpus-cases-medilegal-nz.git
   cd corpus-cases-medilegal-nz
   pixi install
   ```
3. Run code quality checks:
   ```bash
   pixi run check
   ```

## Code Quality Standards

We enforce strict quality rules:
- **Formatting & Linting:** Enforced by `ruff`. Line length is strictly limited to 100 characters.
- **Type Safety:** Enforced via `pyright` in strict mode.
- **Test Coverage:** All Python ingestion wrappers must maintain **>90% test coverage**.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
