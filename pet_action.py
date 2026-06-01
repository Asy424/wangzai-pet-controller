from __future__ import annotations

import argparse
import json
import urllib.request


VALID_STATES = {
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger a local Codex pet action.")
    parser.add_argument("state", nargs="?", default="failed", choices=sorted(VALID_STATES))
    parser.add_argument("duration", nargs="?", type=int, default=1600, help="Duration in ms.")
    parser.add_argument("--url", default="http://127.0.0.1:7777/state", help="Controller /state URL.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.dumps({"state": args.state, "duration": args.duration}).encode("utf-8")
    request = urllib.request.Request(
        args.url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=2) as response:
        print(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
