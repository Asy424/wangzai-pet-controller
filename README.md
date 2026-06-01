# Wangzai Pet Controller

A small Windows-friendly local controller for the Codex pet `wangzai`.

It opens the installed Wangzai spritesheet in a floating desktop window and exposes a tiny localhost API so you can trigger Codex pet states such as `failed`, `waiting`, `review`, and `running-left`.

## Prerequisites

- Wangzai already installed as a Codex/Petdex pet

The controller expects this file by default:

```text
~/.codex/pets/wangzai/spritesheet.webp
```

If your Codex home is on another drive, set `CODEX_HOME` before launching:

```powershell
$env:CODEX_HOME = "D:\Your\CodexHome"
.\dist\WangzaiMenu.exe
```

If you use `WangzaiMenu.exe`, you do not need to install Python or Pillow.

If you use the source scripts, install dependencies:

```powershell
pip install -r requirements.txt
```

## Easiest Use

Download `WangzaiMenu.exe` from this repository's release or `dist` folder, then double-click it.

If you downloaded the source code instead, double-click:

```text
wangzai-menu.bat
```

Then choose an action by typing a number.

```text
1. failed
2. jumping
3. running-left
4. running-right
5. waiting
6. review
7. waving
8. running
9. idle
0. exit
```

The menu starts the floating pet automatically.

## Mobile Web Version

The `web/` folder contains a phone-friendly PWA version.

After GitHub Pages is enabled, open:

```text
https://asy424.github.io/wangzai-pet-controller/web/
```

On mobile, tap an action button to play Wangzai:

```text
失败 / 跳跃 / 向左跑 / 向右跑 / 等待 / 审阅 / 挥手 / 工作中 / 待机
```

This web version includes its own `assets/spritesheet.webp`, so phones do not need Codex, Python, or the Windows exe.

## Use From PowerShell

Start the floating pet:

```powershell
.\wangzai.ps1 start
```

Check that the local controller is running:

```powershell
.\wangzai.ps1 health
```

Trigger actions:

```powershell
.\wangzai.ps1 failed
.\wangzai.ps1 jumping
.\wangzai.ps1 running-left
.\wangzai.ps1 waiting
.\wangzai.ps1 review
```

Set a custom duration in milliseconds:

```powershell
.\wangzai.ps1 failed 3000
```

On Codex Desktop, `wangzai.ps1` will try to use the bundled Codex Python runtime automatically. If `python` is not on your PATH and no bundled runtime is available, set `WANGZAI_PYTHON` first:

```powershell
$env:WANGZAI_PYTHON = "C:\Path\To\python.exe"
.\wangzai.ps1 start
```

## Use Directly With Python

Start the controller:

```powershell
python .\wangzai_pet_controller.py
```

Trigger an action:

```powershell
python .\pet_action.py failed 2200
```

Available actions:

```text
idle
running
waiting
review
failed
waving
jumping
running-left
running-right
```

## Custom Spritesheet

You can point the controller at a specific spritesheet:

```powershell
python .\wangzai_pet_controller.py --spritesheet "C:\Path\To\spritesheet.webp"
```

The spritesheet must follow the Codex pet atlas layout: 8 columns, 9 rows, 192x208 pixels per cell.

## Notes

- The local API listens on `http://127.0.0.1:7777/state`.
- Double-click the floating pet to close it.
- Drag the pet with the left mouse button to move it.
- This repository does not include `pet.json` or `spritesheet.webp`; install Wangzai from Petdex/Codex first.
