# ExperimentGuard — A/B Testing & Experiment Decision Intelligence Platform

ExperimentGuard is a Python-based experimentation platform designed to manage A/B tests, assign users consistently to experiment variants, measure performance, and eventually support statistically informed business decisions.

The project is being developed incrementally, with an emphasis on reproducibility, reliable experiment management, automated testing, and production-oriented architecture.

## Project Status

**Phase 1 — Synthetic Data & Baseline Analytics:** Complete  
**Phase 2 — Experiment Management, Assignment Engine & REST API:** Complete  
**Phase 3 — PostgreSQL Persistence & Event Tracking:** Next

**Latest verification:** 25 automated tests passing.

## Features Implemented

### Phase 1 — Data Generation and Baseline Analytics

- Generate synthetic A/B experiment data for 20,000 users.
- Validate required columns and missing values.
- Detect duplicate user IDs.
- Validate variant labels and conversion values.
- Calculate users and conversions per variant.
- Calculate conversion rates, absolute differences, and relative lift.

### Phase 2 — Experiment Management

- Create experiments with unique identifiers.
- Define experiment names, variants, traffic allocation weights, and primary metrics.
- Support experiment lifecycle states: `draft`, `running`, `paused`, and `completed`.
- Enforce valid lifecycle transitions.
- Prevent duplicate experiment IDs.
- Protect experiment configurations from accidental mutation.

### Deterministic User Assignment

ExperimentGuard uses SHA-256 hashing to assign users to experiment variants.

Assignment is based on the experiment ID and user ID, enabling:

- Consistent assignments for the same user within an experiment.
- Independent assignments across experiments.
- Configurable traffic allocation, including 50/50 and 70/30 splits.
- Rejection of new assignments when an experiment is not running.

**Current limitation:** Assignments are deterministic but are not yet stored in a database.

### FastAPI REST API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/experiments` | Create a new experiment |
| GET | `/experiments` | List experiments |
| GET | `/experiments/{experiment_id}` | Retrieve experiment details |
| PATCH | `/experiments/{experiment_id}/status` | Update experiment status |
| GET | `/experiments/{experiment_id}/assign/{user_id}` | Retrieve a deterministic variant assignment |

API documentation is available through FastAPI's interactive Swagger UI.

## Technology Stack

- **Language:** Python
- **API Framework:** FastAPI
- **Validation:** Pydantic
- **Data Processing:** pandas, NumPy
- **Statistical Libraries:** SciPy
- **Testing:** pytest, FastAPI TestClient
- **Development:** Git, GitHub

PostgreSQL is planned for Phase 3 and is not yet integrated.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/aasthasheth180-ops/ExperimentGuard-A-B-Testing.git
cd ExperimentGuard-A-B-Testing
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the API

```bash
python -m uvicorn src.experimentguard.api:app --reload
```

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

### 5. Create an Experiment

Use `POST /experiments` with:

```json
{
  "experiment_id": "checkout_v1",
  "name": "Checkout Redesign",
  "variants": {
    "A": 0.5,
    "B": 0.5
  },
  "primary_metric": "purchase_conversion"
}
```

The experiment starts in `draft` status.

### 6. Start the Experiment

Use `PATCH /experiments/checkout_v1/status`:

```json
{
  "status": "running"
}
```

### 7. Assign a User

Call:

```http
GET /experiments/checkout_v1/assign/user_101
```

Example response:

```json
{
  "experiment_id": "checkout_v1",
  "user_id": "user_101",
  "variant": "B"
}
```

Repeated requests for the same experiment and user return the same variant while the experiment is running.

**Note:** Experiment configurations currently exist only in memory. Restarting or reloading the API clears them.

## Automated Testing

Run the complete test suite:

```bash
python -m pytest tests/ -v
```

Latest result:

```text
25 passed
```

The tests cover experiment validation, lifecycle management, configuration immutability, deterministic assignments, traffic allocation, API responses, and error handling.

## Development Roadmap

- [x] Phase 1 — Synthetic Data Generation and Baseline Analytics
- [x] Phase 2 — Experiment Management and Deterministic Assignment
- [x] Phase 2 — FastAPI Endpoints and Automated API Tests
- [ ] Phase 3 — PostgreSQL Database Integration
- [ ] Phase 3 — Persistent Experiment and Assignment Records
- [ ] Phase 3 — Event Tracking and Duplicate Event Prevention
- [ ] Phase 4 — Statistical Significance Engine
- [ ] Phase 5 — Experiment Health Monitoring
- [ ] Phase 6 — Business Decision Recommendations
- [ ] Phase 7 — Interactive Dashboard
- [ ] Phase 8 — Deployment and Production Hardening

## Long-Term Vision

ExperimentGuard aims to become an end-to-end experimentation system that connects experiment setup, traffic allocation, event collection, statistical analysis, experiment health, and business decision support.

The goal is not only to calculate whether variant B outperforms variant A, but also to provide a reliable workflow for deciding whether an experiment should continue, stop, or be rolled out.

## Current Limitations

- Experiments are managed in memory.
- User assignments are not persisted.
- Event tracking is not yet implemented.
- Statistical significance testing is not yet integrated into the platform.
- No deployed dashboard or production API is available yet.

These capabilities are planned for subsequent development phases.