""" Functions to interact with process runs """

import logging
import time

from .process import find_process_id_and_steps

logger = logging.getLogger(__name__)


def get_dashboard_run_id(client, process_id: int, cpr: str) -> int:
    """
    Get the latest run ID for a process + CPR combination.
    """

    logger.info(
        "Fetching run ID for process %s and CPR %s",
        process_id,
        cpr,
    )

    retry_count = 3
    attempt = 1

    while attempt <= retry_count:
        try:
            res = client.get(f"runs/?process_id={process_id}&meta_filter=cpr:{cpr}", timeout=10)

            if 200 <= res.status_code < 300:

                if not res.content:
                    raise ValueError("Empty response body")

                data = res.json()
                items = data.get("items", [])

                if not items:
                    raise ValueError("No run items found")

                return items[0]["id"]

            logger.warning(
                "GET run ID failed (attempt %s/%s) | status=%s | body=%s",
                attempt,
                retry_count,
                res.status_code,
                res.text,
            )

        except ValueError as exc:
            logger.exception(
                "Invalid response when fetching run ID (attempt %s): %s",
                attempt,
                exc,
            )

        except Exception:
            logger.exception(
                "GET run ID request crashed (attempt %s)",
                attempt,
            )

        time.sleep(1)
        attempt += 1

    raise RuntimeError(
        f"Could not fetch dashboard run ID for process_id={process_id}, cpr={cpr}"
    )


def get_process_run_by_cpr(client, process_name: str, cpr: str) -> bool:
    """
    Check if a process run exists for a given CPR.
    """

    process_id, _ = find_process_id_and_steps(client=client, process_name=process_name)

    retry_count = 3
    attempt = 1

    while attempt <= retry_count:
        try:
            res = client.get(
                f"runs/?process_id={process_id}"
                f"&meta_filter=cpr%3A{cpr}"
                f"&order_by=created_at"
                f"&sort_direction=desc"
                f"&page=1&size=100", timeout=10,
            )

            if 200 <= res.status_code < 300:

                if not res.content:
                    return False

                items = res.json().get("items", [])

                return len(items) > 0

            logger.warning(
                "GET runs failed (attempt %s/%s) | status=%s | body=%s",
                attempt,
                retry_count,
                res.status_code,
                res.text,
            )

        except ValueError:
            # JSON decode error
            logger.exception(
                "Invalid JSON response when fetching runs (attempt %s)",
                attempt,
            )

        except Exception:
            # Network / timeout / request crash
            logger.exception(
                "GET runs request crashed (attempt %s)",
                attempt,
            )

        time.sleep(1)
        attempt += 1

    # If we exhausted retries, assume no valid run found
    return False


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
