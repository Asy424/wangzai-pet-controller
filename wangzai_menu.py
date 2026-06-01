from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import wangzai_pet_controller


ROOT = Path(__file__).resolve().parent
CONTROLLER = ROOT / "wangzai_pet_controller.py"
STATE_URL = "http://127.0.0.1:7777/state"
HEALTH_URL = "http://127.0.0.1:7777/health"

MENU = [
    ("1", "失败", "failed", 2200),
    ("2", "跳跃", "jumping", 1800),
    ("3", "向左跑", "running-left", 2200),
    ("4", "向右跑", "running-right", 2200),
    ("5", "等待", "waiting", 2600),
    ("6", "审阅", "review", 2200),
    ("7", "挥手", "waving", 1800),
    ("8", "工作中", "running", 2200),
    ("9", "待机", "idle", 1200),
]


def request_json(url: str, payload: dict[str, object] | None = None, timeout: float = 1.5) -> dict[str, object]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def is_controller_ready() -> bool:
    try:
        response = request_json(HEALTH_URL)
        return response.get("ok") is True
    except (OSError, urllib.error.URLError, TimeoutError):
        return False


def start_controller() -> bool:
    if is_controller_ready():
        return True

    if getattr(sys, "frozen", False):
        command = [sys.executable, "--controller"]
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | 0x08000000
    else:
        command = [sys.executable, str(CONTROLLER)]
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0

    subprocess.Popen(
        command,
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )

    for _ in range(20):
        time.sleep(0.2)
        if is_controller_ready():
            return True
    return False


def trigger(state: str, duration: int) -> bool:
    try:
        request_json(STATE_URL, {"state": state, "duration": duration})
        return True
    except (OSError, urllib.error.URLError, TimeoutError):
        return False


def print_menu() -> None:
    print()
    print("Wangzai 动作菜单")
    print("=" * 20)
    for key, label, _state, _duration in MENU:
        print(f"{key}. {label}")
    print("0. 退出")
    print()


def main() -> None:
    if "--controller" in sys.argv:
        sys.argv = [sys.argv[0]]
        wangzai_pet_controller.main()
        return

    print("正在启动 Wangzai...")
    if not start_controller():
        print()
        print("启动失败：找不到或无法打开 Wangzai 素材。")
        print("请确认已经安装 wangzai，并且存在：")
        print(r"  %USERPROFILE%\.codex\pets\wangzai\spritesheet.webp")
        input("按 Enter 退出...")
        raise SystemExit(1)

    while True:
        print_menu()
        choice = input("请选择动作编号：").strip()
        if choice == "0":
            print("已退出菜单。宠物窗口可双击关闭。")
            return

        selected = next((item for item in MENU if item[0] == choice), None)
        if selected is None:
            print("没有这个编号，请重新选择。")
            continue

        _key, label, state, duration = selected
        if trigger(state, duration):
            print(f"已触发：{label}")
        else:
            print("触发失败，正在尝试重新启动控制器...")
            if start_controller() and trigger(state, duration):
                print(f"已触发：{label}")
            else:
                print("仍然失败，请关闭后重新打开。")


if __name__ == "__main__":
    main()
