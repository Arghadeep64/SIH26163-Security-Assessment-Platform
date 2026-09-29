#!/usr/bin/env bash
set -e

# ============================================================================
# SIH26163 - Security Assessment Platform Linux / Render Entrypoint
# National Technical Research Organisation (NTRO) - Problem Statement 26163
#
# Services Architecture:
#   1. Local World Monitor Target     -> 127.0.0.1:3000 (Internal Loopback)
#   2. Controlled Security Demo Target -> 127.0.0.1:9000 (Internal Loopback)
#   3. Security Assessment Platform   -> 0.0.0.0:${PORT:-8000} (Public Web Interface)
# ============================================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "========================================================================"
echo "  SIH26163 - Security Assessment Platform (Linux / Render Launcher)"
echo "  National Technical Research Organisation (NTRO)"
echo "========================================================================"
echo "[INFO] Project Root : $PROJECT_ROOT"

# Fallback for PORT if not set by Render environment
PORT="${PORT:-8000}"

# Graceful process cleanup handler on termination
cleanup() {
    echo ""
    echo "[INFO] Shutting down background target services..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# 1. Start Local World Monitor Target (Port 3000)
echo "[1/3] Starting Local World Monitor Target on 127.0.0.1:3000..."
python research/run_local_worldmonitor.py 3000 &
WM_PID=$!

# 2. Start Controlled Security Demo Target (Port 9000)
echo "[2/3] Starting Controlled Security Demo Target on 127.0.0.1:9000..."
python -m uvicorn main:app --app-dir demo-target --host 127.0.0.1 --port 9000 &
DEMO_PID=$!

# Allow brief moment for internal loopback daemons to bind
sleep 2

# Verify internal services are running
if ! kill -0 "$WM_PID" 2>/dev/null; then
    echo "[ERROR] Failed to start Local World Monitor target on port 3000."
    exit 1
fi

if ! kill -0 "$DEMO_PID" 2>/dev/null; then
    echo "[ERROR] Failed to start Controlled Demo target on port 9000."
    exit 1
fi

echo "[OK] Local World Monitor target running (PID: $WM_PID)"
echo "[OK] Controlled Demo target running (PID: $DEMO_PID)"

# 3. Start Security Assessment Platform (Main Web Process in Foreground)
echo "[3/3] Launching Security Assessment Platform on 0.0.0.0:$PORT..."
echo "[INFO] Serving REST API (/api) and React Frontend SPA from unified process."
echo "========================================================================"

exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --app-dir backend
