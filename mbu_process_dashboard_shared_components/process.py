""" Functions to interact with processes """

import logging

logger = logging.getLogger(__name__)


def find_process_id_and_steps(client, process_name: str):
    """
    Look up a process and return:
      • its ID
      • its list of process steps

    Args:
        client (ProcessDashboardClient): The shared API client.
        process_name (str): The name of the process.

    Returns:
        tuple: (process_id (str|None), steps (list))
    """

    logger.info("Inside find_process_id_and_steps() - finding for process_name: %s", process_name)

    res = client.get("processes/?page=1&size=100")

    items = res.json().get("items", [])

    for row in items:
        if row.get("name") == process_name:
            return row.get("id"), row.get("steps")

    return None, []


def get_dashboard_process_id(client, process_name: str) -> str:
    """
    Fetch the ID of a process by its name.

    Args:
        client (ProcessDashboardClient): API client.
        process_name (str): Process name.

    Returns:
        str: The process ID.

    Raises:
        StopIteration: If no matching process is found.
    """

    logger.info("Retrieving process ID for name: %s", process_name)

    res = client.get("processes/?include_deleted=false")
    items = res.json().get("items", [])

    process = next(p for p in items if p["name"] == process_name)

    return process["id"]
