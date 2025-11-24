""" Functions to interact with process steps """

import logging

logger = logging.getLogger(__name__)


def get_dashboard_step_id(client, process_id: int, step_name: str) -> int:
    """
    Return a step ID based on process_id + step name.

    Args:
        client (ProcessDashboardClient)
        process_id (int)
        step_name (str)

    Returns:
        int: Step ID.

    Raises:
        StopIteration: If the step is not found.
    """

    logger.info("Looking up step ID for '%s'", step_name)

    res = client.get(f"steps/process/{process_id}?include_deleted=false")
    steps = res.json()

    step = next(s for s in steps if s["name"] == step_name)

    return step["id"]
