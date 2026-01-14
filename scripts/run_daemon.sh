#!/bin/bash
#
# Pokemon AI Auto-Improvement Daemon - Run Script
#
# Usage:
#   ./run_daemon.sh start    - Start daemon in background
#   ./run_daemon.sh stop     - Stop daemon
#   ./run_daemon.sh status   - Show daemon status and learnings
#   ./run_daemon.sh once     - Run single improvement cycle
#   ./run_daemon.sh logs     - Tail the daemon logs
#   ./run_daemon.sh install  - Install as systemd service (Linux)
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAEMON_SCRIPT="$SCRIPT_DIR/auto_improvement_daemon.py"
PID_FILE="$SCRIPT_DIR/daemon.pid"
LOG_DIR="$SCRIPT_DIR/logs"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

start_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Daemon is already running (PID: $PID)"
            return 1
        fi
    fi

    echo "Starting Pokemon AI Auto-Improvement Daemon..."
    nohup python3 "$DAEMON_SCRIPT" > "$LOG_DIR/daemon_stdout.log" 2> "$LOG_DIR/daemon_stderr.log" &
    echo $! > "$PID_FILE"
    echo "Daemon started with PID: $(cat $PID_FILE)"
    echo "Logs: $LOG_DIR/auto_improvement.log"
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Stopping daemon (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            echo "Daemon stopped"
        else
            echo "Daemon not running (stale PID file)"
            rm "$PID_FILE"
        fi
    else
        echo "Daemon is not running (no PID file)"
    fi
}

show_status() {
    echo "========================================"
    echo "Pokemon AI Auto-Improvement Daemon"
    echo "========================================"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Status: RUNNING (PID: $PID)"
            echo ""
            # Show process info
            ps -p "$PID" -o pid,user,%cpu,%mem,etime,command --no-headers
        else
            echo "Status: STOPPED (stale PID file)"
        fi
    else
        echo "Status: STOPPED"
    fi

    echo ""
    echo "--- Learnings Summary ---"
    python3 "$DAEMON_SCRIPT" --status
}

run_once() {
    echo "Running single improvement cycle..."
    python3 "$DAEMON_SCRIPT" --once
}

show_logs() {
    if [ -f "$LOG_DIR/auto_improvement.log" ]; then
        tail -f "$LOG_DIR/auto_improvement.log"
    else
        echo "No log file found. Start the daemon first."
    fi
}

install_service() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Please run with sudo for service installation"
        exit 1
    fi

    SERVICE_FILE="$SCRIPT_DIR/pokemon-ai-improver.service"
    if [ -f "$SERVICE_FILE" ]; then
        cp "$SERVICE_FILE" /etc/systemd/system/
        systemctl daemon-reload
        systemctl enable pokemon-ai-improver
        echo "Service installed! Commands:"
        echo "  sudo systemctl start pokemon-ai-improver"
        echo "  sudo systemctl status pokemon-ai-improver"
        echo "  journalctl -u pokemon-ai-improver -f"
    else
        echo "Service file not found: $SERVICE_FILE"
        exit 1
    fi
}

case "$1" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    status)
        show_status
        ;;
    once)
        run_once
        ;;
    logs)
        show_logs
        ;;
    install)
        install_service
        ;;
    restart)
        stop_daemon
        sleep 2
        start_daemon
        ;;
    *)
        echo "Pokemon AI Auto-Improvement Daemon"
        echo ""
        echo "Usage: $0 {start|stop|status|once|logs|install|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start daemon in background"
        echo "  stop    - Stop running daemon"
        echo "  status  - Show daemon status and learnings"
        echo "  once    - Run single improvement cycle (for testing)"
        echo "  logs    - Tail daemon logs in real-time"
        echo "  install - Install as systemd service (requires sudo)"
        echo "  restart - Restart the daemon"
        ;;
esac
