import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def send_discord_notification(message: str) -> None:
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError(
            "DISCORD_WEBHOOK_URL environment variable is not set."
        )

    payload = {
        "content": message
    }

    request = Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "curl/8.5.0",
            "Accept": "*/*"
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=15) as response:
            if response.status not in (200, 204):
                raise RuntimeError(
                    f"Discord returned unexpected status: {response.status}"
                )

        print("Discord notification sent successfully.")

    except HTTPError as error:
        error_details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Discord webhook error: HTTP {error.code}. "
            f"Details: {error_details}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"Could not connect to Discord: {error.reason}"
        ) from error