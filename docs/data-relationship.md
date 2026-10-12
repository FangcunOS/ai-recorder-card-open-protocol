# Data Relationship: Recorder Card, Phone, and PC

[中文](./data-relationship.zh-CN.md)

Read this before writing a mini program, app, or desktop archive. It fixes where data lives for an AI recorder card, recording card, Bluetooth recorder card, or voice recorder card. Frame layouts stay in the [protocol](./protocol.md) and the [中文协议](./protocol.zh-CN.md). Card bring-up stays in the [bring-up skill](./skill.md).

A WeChat mini program and a standalone app use the same relationship. They differ in cache size and background transfer, not in ownership of the data.

## What each side is

| Side | Role |
| --- | --- |
| Recorder card | Capture source. Holds on-card recordings and the file list |
| Phone | Cache. Holds audio not yet accepted by the PC, plus list metadata |
| PC | Archive. Holds the full audio, corpus text, transcript, and searchable detail |

```text
recorder card --BLE protocol--> phone cache --app sync--> PC archive
      |                                                  ^
      +-------------- BLE protocol (web tester) ---------+
```

The two links are independent:

- **Card ↔ phone and card ↔ PC** use the public BLE protocol. The PC can import directly today through the Web Bluetooth tester.
- **Phone ↔ PC** uses the application's own sync session. Those messages are not recorder-card frames.

The phone may be connected only to the card, or only to the PC.

## What each side stores

| Data | Recorder card | Phone | PC |
| --- | --- | --- | --- |
| Audio file | Original on-card recording | Source file waiting to upload, or cache not yet cleared | Complete audio, authoritative copy |
| List | Filename, time, size | Title, time, customer, sync status | Searchable full entry |
| Corpus / transcript | Not stored | Not kept resident; pulled when the PC is connected | Authoritative copy |
| Customer, title, sync status | Not stored | List metadata | Stored with the audio and corpus |

Match a recording by the filename on the card. A title edited by the user exists only on the phone and the PC. Do not look up the card with that title.

## PC archive directories

The PC's authoritative copies live in `archive/` inside this repository. Audio and corpus stay in separate directories and share the card filename's stem.

| Data | Directory | Example |
| --- | --- | --- |
| PC audio | `archive/audio/` | `archive/audio/note20260710-162938.wav` |
| PC corpus | `archive/corpus/` | `archive/corpus/note20260710-162938.md` |

These directories stay on the local machine. Recordings and corpus text are not committed. Each `.gitkeep` exists so the empty directory remains. Chat bring-up writes imports with `tools/qs668-bringup.py` straight into `archive/audio/`.

## Where one recording lives

| Stage | Card file | Phone audio | Phone list | PC audio | PC corpus |
| --- | --- | --- | --- | --- | --- |
| Card only | Present | Absent | Absent | Absent | Absent |
| Waiting for PC | Present | Present | Waiting | Absent | Absent |
| Syncing / failed | Present | Present | Syncing or failed | Incomplete | Absent |
| Synced, cache remains | Present | Present | Synced | Complete | On the PC when it exists |
| Synced, phone source deleted | Present | Absent | Metadata only | Complete | On the PC when it exists |
| PC imported from the card | Present | Absent | Absent | Complete | On the PC when it exists |

A realtime stream is not in this table until it is saved as a file on the card or the phone. After that, mark it waiting for the PC.

After the PC confirms that the audio is complete, the phone deletes its local source file by default and keeps the title, time, customer, and synced status on the list. The on-card recording stays. Deleting the card file is a separate explicit action, not part of the default sync.

## Phone list states

Use only these four states, so a deleted local file and a failed sync never look the same.

| State | On the phone | Opened detail |
| --- | --- | --- |
| Waiting for PC | Source file | Playable, local preview |
| Synced, cache remains | Source file and metadata | Cached audio plays without the PC. Full corpus waits until the PC is connected |
| Synced, metadata only | Title, time, customer, sync status | Without the PC, show "Connect a computer to view". With the PC, pull the text and transcript on demand and do not keep them resident |
| Syncing / failed | Source file still present | Show progress or retry. Do not present this as deleted |

## Boundaries while building

- Build frames, import files, and control recording from the protocol docs.
- Customer, title, sync status, and corpus text belong to the phone and PC application data. Do not write them back to the recorder card.
- The mini program and the app share this lifecycle. Do not invent a second one.
