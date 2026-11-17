
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv(
    "EXPERIMENTGUARD_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

class APIClientError(Exception):
    """Raised when the ExperimentGuard API request fails."""



def get_experiments(token: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments",
            headers=auth_headers(token),
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise APIClientError(
                "Unexpected API response: expected a list."
            )

        return data

    except requests.RequestException as exc:
        raise APIClientError(
            f"Could not fetch experiments: {exc}"
        ) from exc

    except ValueError as exc:
        raise APIClientError(
            "The API returned invalid JSON."
        ) from exc



def create_experiment(
    experiment_id: str,
    name: str,
    variants: dict[str, float],
    primary_metric: str,
    token: str,
    planned_sample_size: int | None = None,
):

    payload = {
        "experiment_id": experiment_id,
        "name": name,
        "variants": variants,
        "primary_metric": primary_metric,
        "planned_sample_size": planned_sample_size,

    }

    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments",
            headers=auth_headers(token),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        raise APIClientError(
            f"Failed to create experiment: {exc}"
        ) from exc



def get_experiment(experiment_id: str, token: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments/{experiment_id}",
            timeout=10,
            headers=auth_headers(token)
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        raise APIClientError(
            f"Could not fetch experiment details: {exc}"
        ) from exc




def get_experiment_metrics(experiment_id: str, token: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments/{experiment_id}/metrics",
            timeout=10,
            headers=auth_headers(token),
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        raise APIClientError(
            f"Could not fetch experiment metrics: {exc}"
        ) from exc




def get_experiment_health(experiment_id: str, token: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments/{experiment_id}/health",
            timeout=10,
            headers=auth_headers(token),
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        raise APIClientError(
            f"Could not fetch experiment health: {exc}"
        ) from exc



def get_experiment_decision(experiment_id: str, token: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments/{experiment_id}/decision",
            timeout=10,
            headers=auth_headers(token),
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        raise APIClientError(
            f"Could not fetch experiment decision: {exc}"
        ) from exc



def get_experiment_statistics(experiment_id: str, token: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/experiments/{experiment_id}/statistics",
            timeout=10,
            headers=auth_headers(token),
        )

        if response.status_code == 422:
            detail = response.json().get("detail", "")
            if detail == "Both variants must have users.":
                return None

        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        raise APIClientError(
            f"Could not fetch experiment statistics: {exc}"
        ) from exc





def update_experiment_status(
    experiment_id: str,
    new_status: str,
    token: str,
):
    """Update an experiment's lifecycle status."""

    try:
        response = requests.patch(
            f"{API_BASE_URL}/experiments/{experiment_id}/status",
            json={"status": new_status},
            timeout=10,
            headers=auth_headers(token),
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        detail = str(exc)

        if exc.response is not None:
            try:
                detail = exc.response.json().get(
                    "detail", detail
                )
            except ValueError:
                pass

        raise APIClientError(
            f"Could not update experiment status: {detail}"
        ) from exc




def register_user(email: str, password: str):
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()



def login_user(email: str, password: str):
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()



def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def get_current_account(token: str):
    response = requests.get(
        f"{API_BASE_URL}/auth/me",
        headers=auth_headers(token),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
