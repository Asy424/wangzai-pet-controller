from __future__ import annotations

import argparse
import json
import os
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tkinter import Label, Tk

from PIL import Image, ImageTk


CELL_W = 192
CELL_H = 208
TRANSPARENT = "#ff00ff"

ROWS = {
    "idle": (0, [280, 110, 110, 140, 140, 320]),
    "running-right": (1, [120, 120, 120, 120, 120, 120, 120, 220]),
    "running-left": (2, [120, 120, 120, 120, 120, 120, 120, 220]),
    "waving": (3, [140, 140, 140, 280]),
    "jumping": (4, [140, 140, 140, 140, 280]),
    "failed": (5, [140, 140, 140, 140, 140, 140, 140, 240]),
    "waiting": (6, [150, 150, 150, 150, 150, 260]),
    "running": (7, [120, 120, 120, 120, 120, 220]),
    "review": (8, [150, 150, 150, 150, 150, 280]),
}


def default_spritesheet(pet_id: str) -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return codex_home / "pets" / pet_id / "spritesheet.webp"


def load_frames(spritesheet: Path) -> dict[str, list[Image.Image]]:
    sheet = Image.open(spritesheet).convert("RGBA")
    frames: dict[str, list[Image.Image]] = {}
    for state, (row, durations) in ROWS.items():
        frames[state] = [
            sheet.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H))
            for col in range(len(durations))
        ]
    return frames


class StateHandler(BaseHTTPRequestHandler):
    commands: "queue.Queue[tuple[str, int | None]]"
    pet_id: str
    port: int

    def log_message(self, *_args: object) -> None:
        return

    def _json(self, status: int, body: dict[str, object]) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"ok": True, "port": self.port, "pet": self.pet_id})
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if self.path not in {"/state", "/bubble", "/update/handoff"}:
            self._json(404, {"ok": False, "error": "not found"})
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}

        if self.path == "/update/handoff":
            self._json(200, {"ok": True})
            return

        if self.path == "/bubble":
            self.commands.put(("waving", 1200))
            self._json(200, {"ok": True, "state": "waving"})
            return

        state = str(body.get("state", "idle"))
        if state not in ROWS:
            self._json(400, {"ok": False, "error": f"unknown state: {state}"})
            return

        duration = body.get("duration")
        self.commands.put((state, int(duration) if isinstance(duration, (int, float)) else None))
        self._json(200, {"ok": True, "state": state})


def run_server(
    commands: "queue.Queue[tuple[str, int | None]]",
    host: str,
    port: int,
    pet_id: str,
) -> None:
    StateHandler.commands = commands
    StateHandler.pet_id = pet_id
    StateHandler.port = port
    server = ThreadingHTTPServer((host, port), StateHandler)
    server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Wangzai pet action controller.")
    parser.add_argument("--pet-id", default="wangzai", help="Pet id under ~/.codex/pets.")
    parser.add_argument("--spritesheet", type=Path, help="Path to spritesheet.webp or spritesheet.png.")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP listen host.")
    parser.add_argument("--port", type=int, default=7777, help="HTTP listen port.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spritesheet = args.spritesheet or default_spritesheet(args.pet_id)
    if not spritesheet.exists():
        raise SystemExit(
            f"Missing spritesheet: {spritesheet}\n"
            f"Install the pet first, or pass --spritesheet <path>."
        )

    commands: "queue.Queue[tuple[str, int | None]]" = queue.Queue()
    threading.Thread(
        target=run_server,
        args=(commands, args.host, args.port, args.pet_id),
        daemon=True,
    ).start()

    root = Tk()
    root.title(args.pet_id)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg=TRANSPARENT)
    try:
        root.wm_attributes("-transparentcolor", TRANSPARENT)
    except Exception:
        pass

    frames = load_frames(spritesheet)
    photos: dict[str, list[ImageTk.PhotoImage]] = {
        state: [ImageTk.PhotoImage(frame) for frame in state_frames]
        for state, state_frames in frames.items()
    }

    label = Label(root, bg=TRANSPARENT, bd=0)
    label.pack()
    x = root.winfo_screenwidth() - CELL_W - 80
    y = root.winfo_screenheight() - CELL_H - 120
    root.geometry(f"{CELL_W}x{CELL_H}+{x}+{y}")

    drag = {"x": 0, "y": 0}

    def start_drag(event) -> None:
        drag["x"] = event.x
        drag["y"] = event.y

    def do_drag(event) -> None:
        root.geometry(f"+{event.x_root - drag['x']}+{event.y_root - drag['y']}")

    label.bind("<ButtonPress-1>", start_drag)
    label.bind("<B1-Motion>", do_drag)
    label.bind("<Double-Button-1>", lambda _event: root.destroy())

    current_state = "idle"
    current_index = 0
    until = 0.0

    def tick() -> None:
        nonlocal current_state, current_index, until
        try:
            state, duration = commands.get_nowait()
            current_state = state
            current_index = 0
            until = time.monotonic() + (duration or 1600) / 1000
        except queue.Empty:
            if current_state != "idle" and time.monotonic() >= until:
                current_state = "idle"
                current_index = 0

        state_photos = photos[current_state]
        label.configure(image=state_photos[current_index])
        label.image = state_photos[current_index]
        delay = ROWS[current_state][1][current_index]
        current_index = (current_index + 1) % len(state_photos)
        root.after(delay, tick)

    tick()
    print(f"{args.pet_id} controller listening on http://{args.host}:{args.port}/state")
    root.mainloop()


if __name__ == "__main__":
    main()
