# OpenClaw Heartbeat - AI Usage Tracker

Check AI usage tracking services and report if needed.

## Services to Monitor

1. **AI Tracker API** (port 8001)
2. **Auto-tracking daemon** 
3. **Database health**
4. **Cost alerts** (if over thresholds)

## Actions

- If API down → restart
- If auto-tracking stopped → restart  
- If costs spike → alert
- If credits low → notify

---

**This file can be referenced in HEARTBEAT.md for periodic monitoring.**