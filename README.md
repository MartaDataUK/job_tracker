# UK Data Engineering & Analytics Job Tracker Pipeline

An automated, AI-augmented data engineering pipeline designed to aggregate, layout-clean, programmatically filter, and mathematically score job listings from multiple UK platforms (LinkedIn, Adzuna, I plan to add more in the future).

The system isolates prime Analytics Engineering, Data Engineering, and Data Contract opportunities while strictly filtering out platform noise, geographic mismatches, and tech-stack anomalies.

## Architecture Overview
The pipeline functions as a lean, multi-stage ETL system:
1. **Extraction:** Scrapers aggregate raw data feeds into source-specific CSV datasets (`linkedin_jobs.csv`, `adzuna_jobs.csv`).
2. **Orchestration (`run_pipeline.py`):**Uses an execution supervisor thread via Python's `subprocess` API to enforce sequence constraints, monitor job exit statuses, and catch run-time exceptions before compiler ingestion.
3. **Transformation & Cleaning (`compile_tracker.py`):** - Runs advanced clean-up routines to strip web-scraping navigation artifacts and visual encoding glitches.
   - Enforces geometric gatekeepers (e.g., accepting all Scotland/local hybrid roles, while aggressively parsing out heavy hybrid multi-day commutes in London/Manchester via custom regex patterns).
4. **Weighted Scoring Engine:** Runs a parameterised multi-variate scoring algorithm to instantly surface prime Inside IR35 contracts with premium day rates, while checking for title-tech stack alignment to eliminate infrastructure/devops anomalies

## Engineering Workflow & AI-Augmented Collaboration
This pipeline was built using a high-velocity, AI-augmented development workflow. Rather than relying on static development patterns, I operated as the **Lead Architect & Systems Engineer**, collaborating with Large Language Models (LLMs) to accelerate the design-to-production lifecycle:

- **Architectural Design & Scoping (Human Lead):** I defined the overarching multi-stage ETL architecture, schema layouts (unifying Adzuna and LinkedIn data streams), tracking states, and strict geographic commuting guardrails.
- **Code Generation & Optimization (AI-Augmented):** Utilized LLMs to rapidly scaffold boilerplate execution blocks, optimize the `openpyxl` formatting layers, and decouple the multi-variate scoring matrix from core processing loops.
- **Edge-Case Isolation & Regex Engineering (Collaborative):** Pair-programmed with LLMs to construct bulletproof regular expressions with precise word-boundary enforcement (`\bpython\b`). This eliminated false positives driven by noisy, unstructured source metadata.
- **Debugging & Edge-Case Safeguards (Human-in-the-Loop):** I isolated critical data-leakage and duplication bugs (such as catching how Excel hyperlinks overwrite raw string variables during incremental reads) and directed the systemic refactoring of the merge state engine.

## Technical Requirements & Setup
- Python 3.10+
- Core Libraries: `pandas`, `openpyxl`

**Pre-requisite Setup Note:** Before executing the main pipeline sequence, you must ensure your local environment contains your respective active API keys for Adzuna and Reed, alongside a valid authentication cookie string for LinkedIn context mapping.

```bash
python run_pipeline.py
