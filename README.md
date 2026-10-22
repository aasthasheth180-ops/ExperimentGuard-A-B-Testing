# ExperimentGuard

**End-to-End A/B Testing & Experiment Decision Intelligence Platform**

ExperimentGuard is a Python-based experimentation platform designed to help product teams run reliable A/B experiments, validate experiment data, analyze performance, and make evidence-based decisions.

## Project Goal

Build an end-to-end platform that supports experiment creation, randomized user assignment, event tracking, statistical analysis, experiment monitoring, and business decision support.

## Current Features — Phase 1

- Reproducible synthetic A/B experiment dataset generation
- Basic experiment data validation
- Conversion rate calculation for control and treatment groups
- Absolute conversion difference and relative lift
- Automated tests using pytest

## Tech Stack

- Python
- Pandas
- NumPy
- SciPy (installed for future statistical analysis)
- Pytest

## Getting Started

Create and activate a Python virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Generate the synthetic experiment dataset:

```powershell
python -m src.experimentguard.data_generation
```

Analyze the experiment:

```powershell
python -m src.experimentguard.analysis
```

Run automated tests:

```powershell
python -m pytest tests/ -v
```

## Sample Experiment Results

| Metric | Control A | Treatment B |
|---|---:|---:|
| Users | 9,938 | 10,062 |
| Conversions | 803 | 920 |
| Conversion rate | 8.08% | 9.14% |

**Observed relative lift:** +13.16%

These results come from synthetic data. Statistical significance and business impact have not yet been evaluated.

## Roadmap

- [x] **Phase 1:** Project foundation and basic experiment analysis
- [ ] **Phase 2:** Experiment management and user assignment
- [ ] **Phase 3:** Event tracking and PostgreSQL
- [ ] **Phase 4:** Statistical analysis engine
- [ ] **Phase 5:** Experiment health monitoring
- [ ] **Phase 6:** Business decision intelligence
- [ ] **Phase 7:** Interactive dashboard
- [ ] **Phase 8:** Deployment and production engineering

## Project Status

**Current Phase:** Phase 1 — Implementation Complete

**Completed:**
- Project setup and Git initialization
- Python virtual environment and dependency setup
- Synthetic A/B experiment data generation
- Experiment data validation
- Conversion rate and relative lift calculations
- Automated testing (3 tests passed)

**Next Phase:** Phase 2 — Experiment Management and Randomized User Assignment

**Overall Progress:** 1 of 8 development phases implemented (12.5%).
