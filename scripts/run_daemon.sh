#!/bin/bash
#
# Pokemon AI Auto-Improvement Daemons - Run Script
#
# Two daemons available:
#   1. Image Improvement - Continuously improves prompts using Claude Vision
#   2. Code Improvement - Continuously improves codebase using Claude API
#
# 24/7 Auto-Restart Options:
#   ./run_daemon.sh watchdog       - Start watchdog (auto-restarts crashed daemons)
#   ./run_daemon.sh supervisor     - Use supervisord for process management
#
# Basic Usage:
#   ./run_daemon.sh image start    - Start image improvement daemon
#   ./run_daemon.sh code start     - Start code improvement daemon
#   ./run_daemon.sh all start      - Start both daemons
#   ./run_daemon.sh status         - Show status of all daemons
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Daemon configurations
IMAGE_DAEMON="$SCRIPT_DIR/auto_improvement_daemon.py"
IMAGE_PID="$SCRIPT_DIR/image_daemon.pid"
IMAGE_LOG="$LOG_DIR/auto_improvement.log"

CODE_DAEMON="$SCRIPT_DIR/code_improvement_daemon.py"
CODE_PID="$SCRIPT_DIR/code_daemon.pid"
CODE_LOG="$LOG_DIR/code_improvement.log"

WATCHDOG="$SCRIPT_DIR/watchdog.py"
WATCHDOG_PID="$SCRIPT_DIR/watchdog.pid"
WATCHDOG_LOG="$LOG_DIR/watchdog.log"

BRAIN="$SCRIPT_DIR/autonomous_brain.py"
BRAIN_PID="$SCRIPT_DIR/brain.pid"
BRAIN_LOG="$LOG_DIR/autonomous_brain.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# ============================================================
# AUTONOMOUS BRAIN (Fully Autonomous AI)
# ============================================================
start_brain() {
    if [ -f "$BRAIN_PID" ] && ps -p "$(cat $BRAIN_PID)" > /dev/null 2>&1; then
        echo "Brain already running (PID: $(cat $BRAIN_PID))"
        return 1
    fi

    # Stop other daemons - brain replaces them
    stop_watchdog 2>/dev/null
    stop_daemon "$IMAGE_PID" "Image" 2>/dev/null
    stop_daemon "$CODE_PID" "Code" 2>/dev/null

    echo "🧠 Starting Autonomous Brain..."
    echo "   Using: Haiku (fast) → Opus 4.5 (decisions) → Sonnet (code)"
    echo ""
    nohup python3 "$BRAIN" > "$LOG_DIR/brain_stdout.log" 2> "$LOG_DIR/brain_stderr.log" &
    echo $! > "$BRAIN_PID"
    echo "Brain started (PID: $(cat $BRAIN_PID))"
    echo ""
    echo "✅ Fully autonomous AI improvement system active!"
    echo "📋 Monitor with: $0 brain logs"
}

stop_brain() {
    if [ -f "$BRAIN_PID" ]; then
        PID=$(cat "$BRAIN_PID")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Stopping brain (PID: $PID)..."
            kill "$PID"
            sleep 2
            if ps -p "$PID" > /dev/null 2>&1; then
                kill -9 "$PID" 2>/dev/null
            fi
            rm "$BRAIN_PID"
            echo "Brain stopped"
        else
            echo "Brain not running (stale PID)"
            rm "$BRAIN_PID"
        fi
    else
        echo "Brain not running"
    fi
}

# ============================================================
# WATCHDOG FUNCTIONS (24/7 Auto-Restart)
# ============================================================
start_watchdog() {
    if [ -f "$WATCHDOG_PID" ] && ps -p "$(cat $WATCHDOG_PID)" > /dev/null 2>&1; then
        echo "Watchdog already running (PID: $(cat $WATCHDOG_PID))"
        return 1
    fi

    # Stop any existing daemons first
    stop_daemon "$IMAGE_PID" "Image" 2>/dev/null
    stop_daemon "$CODE_PID" "Code" 2>/dev/null

    echo "🐕 Starting Watchdog (24/7 auto-restart mode)..."
    nohup python3 "$WATCHDOG" > "$LOG_DIR/watchdog_stdout.log" 2> "$LOG_DIR/watchdog_stderr.log" &
    echo $! > "$WATCHDOG_PID"
    echo "Watchdog started (PID: $(cat $WATCHDOG_PID))"
    echo ""
    echo "✅ Daemons will now auto-restart if they crash!"
    echo "📋 Monitor with: tail -f $WATCHDOG_LOG"
}

stop_watchdog() {
    if [ -f "$WATCHDOG_PID" ]; then
        PID=$(cat "$WATCHDOG_PID")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Stopping watchdog (PID: $PID)..."
            kill "$PID"
            sleep 2
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                kill -9 "$PID" 2>/dev/null
            fi
            rm "$WATCHDOG_PID"
            echo "Watchdog stopped (daemons also stopped)"
        else
            echo "Watchdog not running (stale PID)"
            rm "$WATCHDOG_PID"
        fi
    else
        echo "Watchdog not running"
    fi
}

# ============================================================
# SUPERVISOR FUNCTIONS
# ============================================================
start_supervisor() {
    if ! command -v supervisord &> /dev/null; then
        echo "Supervisor not installed. Installing..."
        pip install supervisor
    fi

    echo "Starting Supervisor..."
    supervisord -c "$SCRIPT_DIR/supervisor.conf"
    echo ""
    echo "✅ Supervisor started! Commands:"
    echo "   supervisorctl -c $SCRIPT_DIR/supervisor.conf status"
    echo "   supervisorctl -c $SCRIPT_DIR/supervisor.conf restart all"
    echo "   supervisorctl -c $SCRIPT_DIR/supervisor.conf tail -f image_daemon"
}

stop_supervisor() {
    if [ -f "$SCRIPT_DIR/supervisord.pid" ]; then
        echo "Stopping Supervisor..."
        supervisorctl -c "$SCRIPT_DIR/supervisor.conf" shutdown
    else
        echo "Supervisor not running"
    fi
}

supervisor_status() {
    supervisorctl -c "$SCRIPT_DIR/supervisor.conf" status
}

start_image_daemon() {
    if [ -f "$IMAGE_PID" ] && ps -p "$(cat $IMAGE_PID)" > /dev/null 2>&1; then
        echo "Image daemon already running (PID: $(cat $IMAGE_PID))"
        return 1
    fi
    echo "Starting Image Improvement Daemon..."
    nohup python3 "$IMAGE_DAEMON" > "$LOG_DIR/image_stdout.log" 2> "$LOG_DIR/image_stderr.log" &
    echo $! > "$IMAGE_PID"
    echo "Image daemon started (PID: $(cat $IMAGE_PID))"
}

start_code_daemon() {
    if [ -f "$CODE_PID" ] && ps -p "$(cat $CODE_PID)" > /dev/null 2>&1; then
        echo "Code daemon already running (PID: $(cat $CODE_PID))"
        return 1
    fi
    echo "Starting Code Improvement Daemon..."
    nohup python3 "$CODE_DAEMON" > "$LOG_DIR/code_stdout.log" 2> "$LOG_DIR/code_stderr.log" &
    echo $! > "$CODE_PID"
    echo "Code daemon started (PID: $(cat $CODE_PID))"
}

stop_daemon() {
    local pid_file=$1
    local name=$2
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Stopping $name daemon (PID: $PID)..."
            kill "$PID"
            rm "$pid_file"
            echo "$name daemon stopped"
        else
            echo "$name daemon not running (stale PID)"
            rm "$pid_file"
        fi
    else
        echo "$name daemon not running"
    fi
}

show_status() {
    echo "========================================"
    echo "  Pokemon AI Auto-Improvement Daemons"
    echo "========================================"
    echo ""

    # Image daemon status
    echo "📷 IMAGE IMPROVEMENT DAEMON"
    if [ -f "$IMAGE_PID" ] && ps -p "$(cat $IMAGE_PID)" > /dev/null 2>&1; then
        echo "   Status: ✅ RUNNING (PID: $(cat $IMAGE_PID))"
        ps -p "$(cat $IMAGE_PID)" -o %cpu,%mem,etime --no-headers | xargs echo "   Resources: CPU:"
    else
        echo "   Status: ⏹️  STOPPED"
    fi
    echo ""
    python3 "$IMAGE_DAEMON" --status 2>/dev/null || echo "   (No data yet)"
    echo ""

    # Code daemon status
    echo "💻 CODE IMPROVEMENT DAEMON"
    if [ -f "$CODE_PID" ] && ps -p "$(cat $CODE_PID)" > /dev/null 2>&1; then
        echo "   Status: ✅ RUNNING (PID: $(cat $CODE_PID))"
        ps -p "$(cat $CODE_PID)" -o %cpu,%mem,etime --no-headers | xargs echo "   Resources: CPU:"
    else
        echo "   Status: ⏹️  STOPPED"
    fi
    echo ""
    python3 "$CODE_DAEMON" --status 2>/dev/null || echo "   (No data yet)"
    echo ""
    echo "========================================"
}

show_logs() {
    local log_type=$1
    case "$log_type" in
        image)
            tail -f "$IMAGE_LOG" 2>/dev/null || echo "No image log found"
            ;;
        code)
            tail -f "$CODE_LOG" 2>/dev/null || echo "No code log found"
            ;;
        *)
            echo "Tailing all logs (Ctrl+C to stop)..."
            tail -f "$IMAGE_LOG" "$CODE_LOG" 2>/dev/null
            ;;
    esac
}

# Main command handling
case "$1" in
    image)
        case "$2" in
            start)
                start_image_daemon
                ;;
            stop)
                stop_daemon "$IMAGE_PID" "Image"
                ;;
            once)
                python3 "$IMAGE_DAEMON" --once
                ;;
            status)
                python3 "$IMAGE_DAEMON" --status
                ;;
            logs)
                tail -f "$IMAGE_LOG"
                ;;
            *)
                echo "Usage: $0 image {start|stop|once|status|logs}"
                ;;
        esac
        ;;
    code)
        case "$2" in
            start)
                start_code_daemon
                ;;
            stop)
                stop_daemon "$CODE_PID" "Code"
                ;;
            once)
                python3 "$CODE_DAEMON" --once
                ;;
            status)
                python3 "$CODE_DAEMON" --status
                ;;
            apply)
                python3 "$CODE_DAEMON" --apply
                ;;
            logs)
                tail -f "$CODE_LOG"
                ;;
            *)
                echo "Usage: $0 code {start|stop|once|status|apply|logs}"
                ;;
        esac
        ;;
    all)
        case "$2" in
            start)
                start_image_daemon
                start_code_daemon
                ;;
            stop)
                stop_daemon "$IMAGE_PID" "Image"
                stop_daemon "$CODE_PID" "Code"
                ;;
            *)
                echo "Usage: $0 all {start|stop}"
                ;;
        esac
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    # ============================================================
    # 24/7 AUTO-RESTART OPTIONS
    # ============================================================
    watchdog)
        case "$2" in
            start|"")
                start_watchdog
                ;;
            stop)
                stop_watchdog
                ;;
            logs)
                tail -f "$WATCHDOG_LOG"
                ;;
            *)
                echo "Usage: $0 watchdog {start|stop|logs}"
                ;;
        esac
        ;;
    supervisor)
        case "$2" in
            start|"")
                start_supervisor
                ;;
            stop)
                stop_supervisor
                ;;
            status)
                supervisor_status
                ;;
            *)
                echo "Usage: $0 supervisor {start|stop|status}"
                ;;
        esac
        ;;
    # ============================================================
    # AUTONOMOUS BRAIN (Best - Full AI Control)
    # ============================================================
    brain)
        case "$2" in
            start|"")
                start_brain
                ;;
            stop)
                stop_brain
                ;;
            once)
                python3 "$BRAIN" --once
                ;;
            status)
                python3 "$BRAIN" --status
                ;;
            logs)
                tail -f "$BRAIN_LOG"
                ;;
            *)
                echo "Usage: $0 brain {start|stop|once|status|logs}"
                ;;
        esac
        ;;
    *)
        echo "========================================"
        echo "  Pokemon AI Auto-Improvement System"
        echo "========================================"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "🧠 AUTONOMOUS BRAIN (Best - Fully Autonomous):"
        echo "  brain [start|stop|once|status|logs]"
        echo "    Uses: Haiku (fast) → Opus 4.5 (decisions) → Sonnet (code)"
        echo "    Auto-decides AND auto-applies improvements!"
        echo ""
        echo "🔥 24/7 AUTO-RESTART:"
        echo "  watchdog [start|stop|logs]  - Monitors & restarts daemons"
        echo "  supervisor [start|stop]     - Professional process manager"
        echo ""
        echo "📦 Manual Control:"
        echo "  image {start|stop|once|status|logs}"
        echo "  code {start|stop|once|status|apply|logs}"
        echo "  all {start|stop}"
        echo "  status  - Show all daemon status"
        echo "  logs    - Tail all logs"
        echo ""
        echo "Examples:"
        echo "  $0 brain              # 🧠 Best: Fully autonomous AI ⭐"
        echo "  $0 watchdog           # Auto-restart daemons"
        echo "  $0 brain status       # Check brain learning progress"
        echo "  $0 status             # Check all status"
        echo ""
        ;;
esac
