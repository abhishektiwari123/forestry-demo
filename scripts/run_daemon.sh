#!/bin/bash
#
# Pokemon AI Auto-Improvement Daemons - Run Script
#
# Two daemons available:
#   1. Image Improvement - Continuously improves prompts using Claude Vision
#   2. Code Improvement - Continuously improves codebase using Claude API
#
# Usage:
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

# Ensure log directory exists
mkdir -p "$LOG_DIR"

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
    *)
        echo "========================================"
        echo "  Pokemon AI Auto-Improvement Daemons"
        echo "========================================"
        echo ""
        echo "Usage: $0 <daemon> <command>"
        echo ""
        echo "Daemons:"
        echo "  image  - Image/prompt improvement using Claude Vision"
        echo "  code   - Codebase improvement using Claude API"
        echo "  all    - Both daemons"
        echo ""
        echo "Commands:"
        echo "  start  - Start daemon in background"
        echo "  stop   - Stop running daemon"
        echo "  once   - Run single improvement cycle"
        echo "  status - Show daemon status"
        echo "  logs   - Tail daemon logs"
        echo ""
        echo "Code daemon also supports:"
        echo "  apply  - Interactively apply pending code changes"
        echo ""
        echo "Examples:"
        echo "  $0 image start     # Start image improvement daemon"
        echo "  $0 code start      # Start code improvement daemon"
        echo "  $0 all start       # Start both daemons"
        echo "  $0 status          # Show status of all daemons"
        echo "  $0 code apply      # Review and apply pending code changes"
        echo "  $0 logs            # Tail all logs"
        echo ""
        ;;
esac
