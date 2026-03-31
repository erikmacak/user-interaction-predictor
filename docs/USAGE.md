# Usage Guide

## Dashboard

- Monitor active agents

---

## Agents

- Create / Update / Delete agents
- Assign audit scenarios
- Export collected data

---

## Sessions

- Manage audit sessions

---

## Key Rules When Providing Video Metadata

### Duration

- Must be **rounded up**
- Example:
  - 16.3 → 17

---

### Description

- Single paragraph
- No line breaks

---

## Prediction Execution

Call: `POST /predict_actions`

Agent must:
- Wait for response
- Execute returned actions
- Continue playback if required