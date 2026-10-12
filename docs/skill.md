# QS668 AI Recorder Card Bring-up Skill

[中文](./skill.zh-CN.md)

This document tells maintainers where the Codex and Cursor bring-up skill lives and what it covers. Frame bytes stay in the [protocol](./protocol.md) and the [中文协议](./protocol.zh-CN.md). Agent steps stay in [SKILL.md](../.agents/skills/qs668-bringup/SKILL.md).

## Files

| File | Audience |
| --- | --- |
| `.agents/skills/qs668-bringup/SKILL.md` | Cursor and Codex |
| `tools/qs668-bringup.py` | CLI host invoked from chat |
| `tools/qs668_protocol.py` | Frame helpers used by the CLI |
| `docs/skill.md` | Maintainers (English) |
| `docs/skill.zh-CN.md` | Maintainers (Chinese) |

Cursor and Codex scan `.agents/skills/` when this repository is open and load `qs668-bringup`. Do not keep another copy under `.cursor/skills/` or `.codex/skills/`.

## Use it in an application repository

Copy `.agents/skills/qs668-bringup/` into the application repository:

```text
your-app/.agents/skills/qs668-bringup/SKILL.md
```

That repository needs the protocol docs, the JavaScript SDK, and the helpers used by `tools/qs668-bringup.py`, or copies of them.

## Primary path: CLI

The skill treats the CLI as the Done path. Audio is written straight to `archive/audio/`:

```bash
python -m pip install -r tools/requirements.txt
python tools/qs668-bringup.py --scan
python tools/qs668-bringup.py --address <ADDR> --import-first --out archive/audio
```

Recording control: `--record-state`, `--record start|pause|resume|save`. Realtime audio: `--realtime 5`. Do not run import and realtime together.

The first connection may still need a person to power the card and allow system Bluetooth. After success, the address is cached in `.qs668-device`. The web tester is only a manual check; the browser download folder is not the Done path.

## Paths the skill covers

1. Read status: battery, capacity, and firmware version.
2. Control recording, and receive hardware key events when AE23 is present.
3. Read the file list, or receive realtime audio. Do not run both transfers at the same time.

The done criteria are in the Done section of `SKILL.md`: the CLI reads battery, lists files, imports one file with a single full write into `archive/audio/`, leaves `archive/corpus/` empty, and never deletes on-card files.

Realtime transcription, segment import, and the authorization code are outside this skill's required scope. Run realtime audio only when the user asks for it, and wrap raw OPUS with `tools/qs668-raw-opus-to-ogg.py`.

Where the phone, PC, and recorder card each keep data is described in [Data relationship](./data-relationship.md).

## Maintenance

- When skill behavior changes, update `SKILL.md`, `docs/skill.md`, and `docs/skill.zh-CN.md` together.
- When commands or frame layouts change, update the protocol docs. Do not add a second command table here.
- After Python helper changes, run `python tools/test_qs668_protocol.py`.
- After JavaScript SDK changes, run `npm test` from the repository root.
