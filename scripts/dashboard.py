#!/usr/bin/env python3
"""
Pokemon AI - System Dashboard

A real-time dashboard to monitor:
- Autonomous Brain status & improvements
- Cost tracking & budget
- YouTube upload status
- Daemon health
- Recent activity logs

Run with: streamlit run scripts/dashboard.py
"""

import streamlit as st
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import os

# Setup paths
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"

# Data files
BRAIN_STATE_FILE = SCRIPT_DIR / "brain_state.json"
COST_FILE = SCRIPT_DIR / "cost_tracking.json"
IMPROVEMENTS_FILE = SCRIPT_DIR / "improvements_history.json"
UPLOAD_HISTORY_FILE = SCRIPT_DIR / "youtube_uploads.json"

# Page config
st.set_page_config(
    page_title="Pokemon AI Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .status-ok { color: #00c853; font-weight: bold; }
    .status-warning { color: #ffab00; font-weight: bold; }
    .status-error { color: #ff1744; font-weight: bold; }
    .big-number { font-size: 48px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def load_json_safe(file_path: Path) -> dict:
    """Safely load JSON file."""
    if file_path.exists():
        try:
            with open(file_path) as f:
                return json.load(f)
        except:
            pass
    return {}


def get_process_status(name: str) -> tuple:
    """Check if a process is running."""
    pid_file = SCRIPT_DIR / f"{name}.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process is running
            result = subprocess.run(["ps", "-p", str(pid)], capture_output=True)
            if result.returncode == 0:
                return True, pid
        except:
            pass
    return False, None


def get_recent_logs(log_file: str, lines: int = 20) -> list:
    """Get recent log entries."""
    log_path = LOG_DIR / log_file
    if log_path.exists():
        try:
            with open(log_path) as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except:
            pass
    return []


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.title("🧠 Pokemon AI")
    st.markdown("---")

    # Quick actions
    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("📊 Full Report", use_container_width=True):
            st.session_state.show_report = True

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["Overview", "Brain Status", "Cost Tracking", "YouTube", "Logs"],
        index=0
    )

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")


# =============================================================================
# OVERVIEW PAGE
# =============================================================================
if page == "Overview":
    st.title("📊 System Overview")

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    # Brain status
    brain_running, brain_pid = get_process_status("autonomous_brain")
    with col1:
        st.metric(
            "🧠 Brain",
            "Running" if brain_running else "Stopped",
            delta=f"PID {brain_pid}" if brain_running else None,
            delta_color="normal" if brain_running else "off"
        )

    # Cost status
    cost_data = load_json_safe(COST_FILE)
    monthly_spent = cost_data.get("monthly_spent_usd", 0)
    monthly_limit = 180.0
    with col2:
        st.metric(
            "💰 Monthly Cost",
            f"${monthly_spent:.2f}",
            delta=f"{(monthly_spent/monthly_limit*100):.1f}% of budget"
        )

    # Brain improvements
    brain_state = load_json_safe(BRAIN_STATE_FILE)
    total_improvements = brain_state.get("total_improvements", 0)
    successful = brain_state.get("successful_improvements", 0)
    with col3:
        success_rate = (successful / total_improvements * 100) if total_improvements > 0 else 0
        st.metric(
            "✅ Improvements",
            str(successful),
            delta=f"{success_rate:.0f}% success rate"
        )

    # Watchdog status
    watchdog_running, _ = get_process_status("watchdog")
    with col4:
        st.metric(
            "🐕 Watchdog",
            "Active" if watchdog_running else "Inactive",
            delta="Auto-restart ON" if watchdog_running else "Auto-restart OFF"
        )

    st.markdown("---")

    # Two column layout
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🧠 Brain Activity")

        if brain_state:
            # Quality trend
            quality_trend = brain_state.get("quality_trend", [])
            if quality_trend:
                st.write("**Recent Improvements:**")
                for item in quality_trend[-5:]:
                    file_name = Path(item.get("file", "unknown")).name
                    improvement = item.get("improvement", "")[:50]
                    st.write(f"• `{file_name}`: {improvement}")

            # Learned patterns
            patterns = brain_state.get("learned_patterns", [])
            if patterns:
                with st.expander(f"📚 Learned Patterns ({len(patterns)})"):
                    for p in patterns[-10:]:
                        st.write(f"• {p[:80]}")
        else:
            st.info("No brain activity yet. Start the brain to see data.")

    with right_col:
        st.subheader("💰 Budget Status")

        if cost_data:
            daily_spent = cost_data.get("daily_spent_usd", 0)
            daily_limit = 6.0

            # Progress bars
            st.write("**Daily Budget**")
            daily_pct = min(daily_spent / daily_limit, 1.0)
            st.progress(daily_pct, text=f"${daily_spent:.4f} / ${daily_limit:.2f}")

            st.write("**Monthly Budget**")
            monthly_pct = min(monthly_spent / monthly_limit, 1.0)
            st.progress(monthly_pct, text=f"${monthly_spent:.2f} / ${monthly_limit:.2f}")

            # INR conversion
            inr_spent = monthly_spent * 83
            st.caption(f"Monthly in INR: ₹{inr_spent:.0f} / ₹15,000")

            # Status indicator
            if monthly_pct < 0.8:
                st.success("🟢 Budget OK")
            elif monthly_pct < 0.95:
                st.warning("🟡 Budget Warning (80%+)")
            else:
                st.error("🔴 Budget Critical (95%+)")
        else:
            st.info("No cost data yet.")

    st.markdown("---")

    # Recent activity log
    st.subheader("📋 Recent Activity")
    logs = get_recent_logs("autonomous_brain.log", 10)
    if logs:
        log_text = "".join(logs)
        st.code(log_text, language="text")
    else:
        st.info("No recent logs available.")


# =============================================================================
# BRAIN STATUS PAGE
# =============================================================================
elif page == "Brain Status":
    st.title("🧠 Autonomous Brain Status")

    brain_state = load_json_safe(BRAIN_STATE_FILE)
    brain_running, brain_pid = get_process_status("autonomous_brain")

    # Status header
    col1, col2, col3 = st.columns(3)
    with col1:
        if brain_running:
            st.success(f"✅ Brain Running (PID: {brain_pid})")
        else:
            st.error("❌ Brain Stopped")

    with col2:
        total = brain_state.get("total_improvements", 0)
        success = brain_state.get("successful_improvements", 0)
        st.metric("Total Improvements", total)

    with col3:
        failed = brain_state.get("failed_improvements", 0)
        rate = (success / total * 100) if total > 0 else 0
        st.metric("Success Rate", f"{rate:.1f}%")

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Improvements", "Patterns", "Research"])

    with tab1:
        improvements = load_json_safe(IMPROVEMENTS_FILE)
        if isinstance(improvements, list) and improvements:
            st.write(f"**Total Records:** {len(improvements)}")

            # Recent improvements table
            recent = improvements[-20:]
            for imp in reversed(recent):
                status = "✅" if imp.get("success") else "❌"
                time_str = imp.get("timestamp", "")[:19]
                file_name = Path(imp.get("file", "unknown")).name
                desc = imp.get("improvement", "")[:60]

                with st.container():
                    st.write(f"{status} `{time_str}` | **{file_name}** | {desc}")
        else:
            st.info("No improvement history yet.")

    with tab2:
        learned = brain_state.get("learned_patterns", [])
        avoid = brain_state.get("avoid_patterns", [])

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**✅ Successful Patterns ({len(learned)})**")
            for p in learned[-15:]:
                st.write(f"• {p[:100]}")

        with col2:
            st.write(f"**❌ Failed Patterns ({len(avoid)})**")
            for p in avoid[-15:]:
                st.write(f"• {p[:100]}")

    with tab3:
        research = brain_state.get("last_research_findings", {})
        if research:
            for topic, findings in research.items():
                with st.expander(topic):
                    if isinstance(findings, list):
                        for f in findings:
                            st.json(f)
        else:
            st.info("No research findings yet.")


# =============================================================================
# COST TRACKING PAGE
# =============================================================================
elif page == "Cost Tracking":
    st.title("💰 Cost Tracking & Budget")

    cost_data = load_json_safe(COST_FILE)

    if cost_data:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            daily = cost_data.get("daily_spent_usd", 0)
            st.metric("Today", f"${daily:.4f}", delta=f"of $6.00 limit")

        with col2:
            monthly = cost_data.get("monthly_spent_usd", 0)
            st.metric("This Month", f"${monthly:.4f}", delta=f"of $180.00 limit")

        with col3:
            total = cost_data.get("total_spent_usd", 0)
            st.metric("All Time", f"${total:.4f}")

        with col4:
            inr = monthly * 83
            st.metric("Monthly (INR)", f"₹{inr:.0f}", delta="of ₹15,000 limit")

        st.markdown("---")

        # Budget visualization
        st.subheader("Budget Usage")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Daily Budget (6 USD)**")
            daily_pct = min(cost_data.get("daily_spent_usd", 0) / 6.0 * 100, 100)
            st.progress(daily_pct / 100)
            st.caption(f"{daily_pct:.1f}% used")

        with col2:
            st.write("**Monthly Budget (180 USD / ₹15,000)**")
            monthly_pct = min(cost_data.get("monthly_spent_usd", 0) / 180.0 * 100, 100)
            st.progress(monthly_pct / 100)
            st.caption(f"{monthly_pct:.1f}% used")

        # Quality preservation notice
        st.info("🛡️ **Quality Preservation Enabled**: Critical tasks (security, final decisions) never use cheaper models even when budget is tight.")

        st.markdown("---")

        # Daily breakdown
        st.subheader("Daily Breakdown")
        daily_breakdown = cost_data.get("daily_breakdown", {})
        if daily_breakdown:
            sorted_days = sorted(daily_breakdown.items(), reverse=True)[:14]
            for day, cost in sorted_days:
                st.write(f"• **{day}**: ${cost:.4f}")

        # Recent calls
        st.subheader("Recent API Calls")
        calls = cost_data.get("calls", [])
        if calls:
            for call in calls[-10:]:
                model = call.get("model", "unknown")
                cost = call.get("cost_usd", 0)
                op = call.get("operation", "unknown")
                st.write(f"• `{model}`: ${cost:.4f} ({op})")
    else:
        st.info("No cost data available yet. Start the brain to begin tracking.")


# =============================================================================
# YOUTUBE PAGE
# =============================================================================
elif page == "YouTube":
    st.title("📺 YouTube Upload Status")

    # Check credentials
    creds_file = SCRIPT_DIR / "youtube_oauth.json"
    secrets_file = SCRIPT_DIR / "client_secrets.json"

    col1, col2 = st.columns(2)

    with col1:
        if secrets_file.exists():
            st.success("✅ Client secrets configured")
        else:
            st.error("❌ Client secrets missing")
            st.caption("Download from Google Cloud Console")

    with col2:
        if creds_file.exists():
            st.success("✅ Authenticated")
        else:
            st.warning("⚠️ Not authenticated")
            st.caption("Run: ./scripts/run_daemon.sh youtube auth")

    st.markdown("---")

    # Upload history
    st.subheader("Upload History")
    uploads = load_json_safe(UPLOAD_HISTORY_FILE)

    if isinstance(uploads, list) and uploads:
        st.write(f"**Total uploads:** {len(uploads)}")

        for upload in reversed(uploads[-10:]):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{upload.get('title', 'Untitled')}**")
                with col2:
                    st.write(upload.get('privacy', 'unknown'))
                with col3:
                    video_id = upload.get('video_id', '')
                    if video_id:
                        st.markdown(f"[Watch](https://youtube.com/watch?v={video_id})")

                st.caption(upload.get('timestamp', '')[:19])
                st.markdown("---")
    else:
        st.info("No uploads yet.")

    # Upload form
    st.subheader("Quick Upload")
    with st.form("upload_form"):
        video_file = st.text_input("Video file path")
        title = st.text_input("Title", value="Pokemon AI Battle")
        privacy = st.selectbox("Privacy", ["private", "unlisted", "public"])

        if st.form_submit_button("Upload"):
            if video_file and Path(video_file).exists():
                st.info(f"Upload command: ./scripts/run_daemon.sh youtube upload '{video_file}' --title '{title}' --privacy {privacy}")
            else:
                st.error("Please provide a valid video file path")


# =============================================================================
# LOGS PAGE
# =============================================================================
elif page == "Logs":
    st.title("📋 System Logs")

    # Log file selector
    log_files = list(LOG_DIR.glob("*.log")) if LOG_DIR.exists() else []
    log_names = [f.name for f in log_files]

    if log_names:
        selected_log = st.selectbox("Select log file", log_names)
        lines = st.slider("Number of lines", 10, 100, 30)

        if st.button("🔄 Refresh Logs"):
            st.rerun()

        logs = get_recent_logs(selected_log, lines)
        if logs:
            # Color code by level
            log_text = ""
            for line in logs:
                if "ERROR" in line:
                    log_text += f"🔴 {line}"
                elif "WARNING" in line:
                    log_text += f"🟡 {line}"
                elif "INFO" in line:
                    log_text += f"🟢 {line}"
                else:
                    log_text += line

            st.text_area("Log output", log_text, height=500)
        else:
            st.info("Log file is empty.")
    else:
        st.info("No log files found.")

    # Quick log actions
    st.markdown("---")
    st.subheader("Quick Commands")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.code("./scripts/run_daemon.sh brain logs", language="bash")
    with col2:
        st.code("./scripts/run_daemon.sh cost", language="bash")
    with col3:
        st.code("./scripts/run_daemon.sh status", language="bash")


# Footer
st.markdown("---")
st.caption("Pokemon AI Dashboard | Auto-refresh: use the Refresh button")
