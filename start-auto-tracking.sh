#!/bin/bash
# AI Usage Tracker Auto-Start Script

set -e

TRACKER_DIR="/home/y7/.openclaw/workspace/ai-usage-tracker"
cd "$TRACKER_DIR"

echo "🚀 Starting AI Usage Tracker services..."

# Start API server if not running
if ! pgrep -f "ai-tracker-api.py" > /dev/null; then
    echo "📡 Starting API server on port 8001..."
    python3 ai-tracker-api.py &
    sleep 3
fi

# Start web dashboard if not running
if ! pgrep -f "http.server 8002" > /dev/null; then
    echo "🌐 Starting web dashboard on port 8002..."
    python3 -m http.server 8002 &
    sleep 2
fi

# Start auto-tracking if not running
if ! pgrep -f "openclaw-usage-integration.py --auto-track" > /dev/null; then
    echo "🔄 Starting OpenClaw auto-tracking (every 60 seconds)..."
    python3 openclaw-usage-integration.py --auto-track --interval 60 &
    sleep 2
fi

echo "✅ All AI Usage Tracker services are running!"
echo ""
echo "📊 Dashboard: http://localhost:8002/usage-dashboard.html"
echo "📡 API: http://localhost:8001"
echo "💰 Balance: $(python3 ai-usage-tracker.py balance --json | jq -r '.remaining_credits')"
echo ""