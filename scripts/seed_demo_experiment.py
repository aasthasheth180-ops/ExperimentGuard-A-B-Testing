
import random
import requests

BASE_URL = "http://127.0.0.1:8000"
EXPERIMENT_ID = "demo_checkout_conversion_v1"
TOTAL_USERS = 10_000

rng = random.Random(42)
session = requests.Session()

assigned = {"A": 0, "B": 0}
conversions = {"A": 0, "B": 0}

for i in range(2, TOTAL_USERS + 1):
    user_id = f"demo_user_{i:04d}"

    assignment_response = session.get(
        f"{BASE_URL}/experiments/{EXPERIMENT_ID}/assign/{user_id}",
        timeout=10,
    )
    assignment_response.raise_for_status()

    variant = assignment_response.json()["variant"]
    assigned[variant] += 1

    conversion_probability = 0.08 if variant == "A" else 0.095

    if rng.random() < conversion_probability:
        event_id = f"demo_checkout_conversion_{i:04d}"

        event_response = session.post(
            f"{BASE_URL}/events",
            json={
                "event_id": event_id,
                "experiment_id": EXPERIMENT_ID,
                "user_id": user_id,
                "event_type": "conversion",
                "properties": {"source": "synthetic_demo"},
            },
            timeout=10,
        )

        event_response.raise_for_status()
        conversions[variant] += 1

    if i % 1000 == 0:
        print(f"Processed {i:,} users")

print("\nSynthetic demo generation completed.")
print("Assigned:", assigned)
print("Conversions:", conversions)
