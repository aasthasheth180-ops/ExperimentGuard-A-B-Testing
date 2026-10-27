import hashlib

from .experiment import Experiment


def assign_user(experiment: Experiment, user_id: str) -> str:
    """
    Deterministically assign a user to an experiment variant.

    The same experiment ID and user ID always produce
    the same assignment for an unchanged configuration.
    """

    if experiment.status != "running":
        raise ValueError("Experiment must be running to assign users.")

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("User ID must be a non-empty string.")

    # Create a stable identifier for this experiment-user pair
    assignment_key = f"{experiment.experiment_id}:{user_id}"

    # SHA-256 produces a stable hash across Python sessions
    hash_digest = hashlib.sha256(
        assignment_key.encode("utf-8")
    ).digest()

    # Convert hash into a number between 0 and 1
    hash_value = int.from_bytes(hash_digest, "big")
    bucket = hash_value / (2 ** 256)

    # Select a variant based on traffic allocation
    cumulative_weight = 0.0

    for variant, weight in experiment.variants.items():
        cumulative_weight += weight

        if bucket < cumulative_weight:
            return variant

    # Floating-point safety fallback
    return list(experiment.variants.keys())[-1]