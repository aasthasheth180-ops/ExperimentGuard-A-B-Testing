
import random
import requests

BASE_URL = "http://127.0.0.1:8000"
EXPERIMENT_ID = "sample_size_api_test_v1"
TOTAL_USERS = 12_000
SEED = 42

rng = random.Random(SEED)
session = requests.Session()

assigned = {"A": 0, "B": 0}
conversions = {"A": 0, "B": 0}

# Verify experiment configuration before generating data.
response = session.get(
    f"{BASE_URL}/experiments/{EXPERIMENT_ID}",
    timeout=10,
)
response.raise_for_status()

experiment = response.json()

if experiment["status"] != "running":
    raise RuntimeError(
        "Experiment must be running before seeding."
    )

if experiment.get("planned_sample_size") != TOTAL_USERS:
    raise RuntimeError(
        "Planned sample size does not match TOTAL_USERS."
    )

# Prevent accidentally rerunning against an experiment
# that already contains assignments.
metrics_response = session.get(
    f"{BASE_URL}/experiments/{EXPERIMENT_ID}/metrics",
    timeout=10,
)
metrics_response.raise_for_status()

variant_metrics = metrics_response.json()["variants"]

existing_users = sum(
    int(data.get("assigned_users", 0))
    for data in variant_metrics.values()
)

if existing_users != 0:
    raise RuntimeError(
        f"Experiment already contains {existing_users:,} users. "
        "Seeding aborted to prevent duplicate data."
    )

print(f"Experiment: {EXPERIMENT_ID}")
print(f"Planned sample size: {TOTAL_USERS:,}")
print("Starting synthetic data generation...")

for i in range(1, TOTAL_USERS + 1):
    user_id = f"planned_demo_user_{i:05d}"

    assignment_response = session.get(
        f"{BASE_URL}/experiments/{EXPERIMENT_ID}/assign/{user_id}",
        timeout=10,
    )
    assignment_response.raise_for_status()

    variant = assignment_response.json()["variant"]
    assigned[variant] += 1

    conversion_probability = (
        0.08 if variant == "A" else 0.095
    )

    if rng.random() < conversion_probability:
        event_id = f"planned_demo_conversion_{i:05d}"

        event_response = session.post(
            f"{BASE_URL}/events",
            json={
                "event_id": event_id,
                "experiment_id": EXPERIMENT_ID,
                "user_id": user_id,
                "event_type": "conversion",
                "properties": {
                    "source": "synthetic_planned_demo",
                    "seed": SEED,
                },
            },
            timeout=10,
        )
        event_response.raise_for_status()

        conversions[variant] += 1

    if i % 1000 == 0:
        print(f"Processed {i:,} users")

print("\nSynthetic experiment generation completed.")
print("Assigned:", assigned)
print("Conversions:", conversions)
