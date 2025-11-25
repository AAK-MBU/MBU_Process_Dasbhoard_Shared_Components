""" Functions to interact with process runs """

import logging

from .process import find_process_id_and_steps

logger = logging.getLogger(__name__)


def get_dashboard_run_id(client, process_id: int, cpr: str) -> int:
    """
    Get the latest run ID for a process + CPR combination.

    Args:
        client (ProcessDashboardClient): API client.
        process_id (int): Dashboard process ID.
        cpr (str): Citizen CPR number.

    Returns:
        int: The run ID.

    Raises:
        Exception: If something goes wrong or no items exist.
    """

    logger.info("Fetching run ID for process %s and CPR %s", process_id, cpr)

    res = client.get(f"runs/?process_id={process_id}&meta_filter=cpr:{cpr}")

    return res.json()["items"][0]["id"]


def create_dashboard_run(client, process_name: str, meta: dict):
    """
    Create a new process run.

    Requires meta containing at least:
      • 'cpr'
      • 'name'

    Args:
        client (ProcessDashboardClient)
        process_name (str)
        meta (dict)
    """

    logger.info("Creating process run for %s", process_name)
    logger.info("Metadata: %s", meta)

    process_id, _ = find_process_id_and_steps(client, process_name)

    payload = {
        "entity_id": meta.get("cpr"),
        "entity_name": meta.get("name"),
        "meta": meta,
        "process_id": process_id,
    }

    client.post("runs/", json=payload)
