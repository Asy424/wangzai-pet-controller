# Wangzai Pet Controller

A small Windows-friendly local controller for the Codex pet `wangzai`.

It opens the installed Wangzai spritesheet in a floating desktop window and exposes a tiny localhost API so you can trigger Codex pet states such as `failed`, `waiting`, `review`, and `running-left`.

## Prerequisites

- Python 3.10 or newer
- The Python package `Pillow`
- Wangzai already installed as a Codex/Petdex pet

The controller expects this file by default:

```text
~/.codex/pets/wangzai/spritesheet.webp
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

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

If `python` is not on your PATH, set `WANGZAI_PYTHON` first:

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
