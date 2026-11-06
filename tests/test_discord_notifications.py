from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from discord_notifications import send_discord_notification


if __name__ == "__main__":
    send_discord_notification(
        "Research Library test: Discord notifications are working!"
    )