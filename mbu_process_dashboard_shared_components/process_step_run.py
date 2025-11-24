import logging

from datetime import datetime, timezone

from mbu_rpa_core.exceptions import BusinessError

from .process import get_dashboard_process_id
from .process_step import get_dashboard_step_id
from .process_run import get_dashboard_run_id

logger = logging.getLogger(__name__)


def get_step_run_id_for_process_step_cpr(client, process_name: str, step_name: str, cpr: str) -> int:
    """
    Look up a step-run ID using:
        • process name
        • step name
        • CPR number

    Args:
        client (ProcessDashboardClient)
        process_name (str)
        step_name (str)
        cpr (str)

    Returns:
        int: Step run ID.

    Raises:
        RuntimeError: If the step-run does not exist.
    """

    logger.info("Finding step-run ID for %s / %s / %s", process_name, step_name, cpr)

    process_id = get_dashboard_process_id(client, process_name)
    step_id = get_dashboard_step_id(client, process_id, step_name)
    run_id = get_dashboard_run_id(client, process_id, cpr)

    res = client.get(f"step-runs/run/{run_id}/step/{step_id}?include_deleted=false")
    step_run = res.json()

    step_run_id = step_run.get("id")

    if step_run_id is None:
        raise RuntimeError("Step run ID not found for process/step/CPR combination.")

    return step_run_id


def build_step_run_update(status: str, failure: Exception | None = None) -> dict:
    """
    Build the JSON body used for updating a step run.

    Args:
        status (str): New status ("success", "failed", etc.)
        failure (Exception|None): Error info to include.

    Returns:
        dict: JSON payload for PATCH.
    """

    now = (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

    failure_data = None

    if failure:
        if isinstance(failure, BusinessError):
            failure_data = {
                "error_code": type(failure).__name__,
                "message": str(failure),
                "details": str(failure.__traceback__) if failure.__traceback__ else None,
            }
        else:
            failure_data = {
                "error_code": "ApplicationException",
                "message": "Processen er fejlet",
                "details": (
                    "Digitalisering undersøger fejlen og genstarter processen.\n\n"
                    "Kontakt Digitalisering hvis det ikke er løst efter 2 arbejdsdage."
                ),
            }

    return {
        "status": status,
        "started_at": now,
        "finished_at": now,
        "failure": failure_data,
    }


def update_dashboard_step_run_by_id(client, step_run_id: int, update_data: dict):
    """
    PATCH update a step-run entry in the dashboard.

    Args:
        client (ProcessDashboardClient)
        step_run_id (int)
        update_data (dict)

    Returns:
        tuple: (response_json, status_code)
    """

    logger.info("Updating step run ID %s", step_run_id)

    res = client.patch(f"step-runs/{step_run_id}", json=update_data)

    return res.json(), res.status_code
