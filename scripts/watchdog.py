#!/usr/bin/env python3
"""
Pokemon AI Watchdog - Keeps daemons running 24/7

This watchdog monitors the improvement daemons and automatically
restarts them if they crash. Run this as your main process.

Features:
- Monitors both image and code improvement daemons
- Auto-restarts crashed processes within seconds
- Exponential backoff on repeated failures
- Health checks and logging
- Graceful shutdown handling

Run with: python scripts/watchdog.py
Or use: nohup python scripts/watchdog.py &
"""

import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WATCHDOG - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "watchdog.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Daemon configurations
DAEMONS = {
    "image": {
        "script": SCRIPT_DIR / "auto_improvement_daemon.py",
        "name": "Image Improvement Daemon",
        "process": None,
        "restart_count": 0,
        "last_restart": None,
        "max_restarts_per_hour": 10,
        "backoff_seconds": 5
    },
    "code": {
        "script": SCRIPT_DIR / "code_improvement_daemon.py",
        "name": "Code Improvement Daemon",
        "process": None,
        "restart_count": 0,
        "last_restart": None,
        "max_restarts_per_hour": 10,
        "backoff_seconds": 5
    }
}

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    running = False


def start_daemon(daemon_key: str) -> bool:
    """Start a daemon process."""
    daemon = DAEMONS[daemon_key]
    script = daemon["script"]

    if not script.exists():
        logger.error(f"Script not found: {script}")
        return False

    try:
        # Start the daemon process
        process = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=SCRIPT_DIR
        )

        daemon["process"] = process
        daemon["last_restart"] = datetime.now()
        daemon["restart_count"] += 1

        logger.info(f"✅ Started {daemon['name']} (PID: {process.pid})")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to start {daemon['name']}: {e}")
        return False


def check_daemon(daemon_key: str) -> bool:
    """Check if a daemon is running. Returns True if healthy."""
    daemon = DAEMONS[daemon_key]
    process = daemon["process"]

    if process is None:
        return False

    # Check if process is still running
    poll = process.poll()

    if poll is None:
        # Process is still running
        return True
    else:
        # Process has exited
        logger.warning(f"⚠️ {daemon['name']} exited with code {poll}")
        daemon["process"] = None
        return False


def should_restart(daemon_key: str) -> bool:
    """Check if we should restart based on backoff rules."""
    daemon = DAEMONS[daemon_key]

    # Reset restart count every hour
    if daemon["last_restart"]:
        if datetime.now() - daemon["last_restart"] > timedelta(hours=1):
            daemon["restart_count"] = 0

    # Check if we've exceeded max restarts
    if daemon["restart_count"] >= daemon["max_restarts_per_hour"]:
        logger.error(f"🚫 {daemon['name']} exceeded max restarts per hour. Waiting...")
        return False

    return True


def get_backoff_time(daemon_key: str) -> int:
    """Calculate exponential backoff time."""
    daemon = DAEMONS[daemon_key]
    base = daemon["backoff_seconds"]
    count = min(daemon["restart_count"], 6)  # Cap at 6 for max ~5 min backoff
    return base * (2 ** count)


def stop_all_daemons():
    """Stop all running daemons gracefully."""
    for daemon_key, daemon in DAEMONS.items():
        process = daemon["process"]
        if process and process.poll() is None:
            logger.info(f"Stopping {daemon['name']} (PID: {process.pid})...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {daemon['name']}...")
                process.kill()
            daemon["process"] = None


def print_status():
    """Print current status of all daemons."""
    print("\n" + "=" * 50)
    print("  Pokemon AI Watchdog - Status")
    print("=" * 50)

    for daemon_key, daemon in DAEMONS.items():
        process = daemon["process"]
        status = "✅ RUNNING" if process and process.poll() is None else "❌ STOPPED"
        pid = process.pid if process else "N/A"
        restarts = daemon["restart_count"]

        print(f"\n{daemon['name']}:")
        print(f"  Status: {status}")
        print(f"  PID: {pid}")
        print(f"  Restarts this hour: {restarts}")

    print("\n" + "=" * 50)


def run_watchdog():
    """Main watchdog loop."""
    global running

    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("=" * 60)
    logger.info("🐕 Pokemon AI Watchdog Starting")
    logger.info("=" * 60)

    # Initial startup of all daemons
    for daemon_key in DAEMONS:
        start_daemon(daemon_key)
        time.sleep(2)  # Stagger startup

    check_interval = 10  # Check every 10 seconds
    status_interval = 300  # Print status every 5 minutes
    last_status = datetime.now()

    while running:
        try:
            # Check each daemon
            for daemon_key in DAEMONS:
                if not check_daemon(daemon_key):
                    if should_restart(daemon_key):
                        backoff = get_backoff_time(daemon_key)
                        logger.info(f"⏳ Waiting {backoff}s before restarting {DAEMONS[daemon_key]['name']}...")
                        time.sleep(backoff)

                        if running:  # Check again after sleep
                            start_daemon(daemon_key)

            # Periodic status log
            if datetime.now() - last_status > timedelta(seconds=status_interval):
                for daemon_key, daemon in DAEMONS.items():
                    process = daemon["process"]
                    if process and process.poll() is None:
                        logger.info(f"💚 {daemon['name']} healthy (PID: {process.pid})")
                last_status = datetime.now()

            time.sleep(check_interval)

        except Exception as e:
            logger.error(f"Watchdog error: {e}")
            time.sleep(check_interval)

    # Graceful shutdown
    logger.info("Shutting down all daemons...")
    stop_all_daemons()
    logger.info("🐕 Watchdog stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pokemon AI Watchdog")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    args = parser.parse_args()

    if args.status:
        print_status()
    else:
        run_watchdog()
