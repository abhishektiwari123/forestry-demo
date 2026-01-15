#!/usr/bin/env python3
"""
Pokemon AI - Autonomous Brain 🧠

A fully autonomous AI system that continuously improves the codebase
using the best AI models for each task:

- Claude Haiku: Fast image analysis, quick decisions
- Claude Opus 4.5: Complex code improvements, architecture decisions
- Claude Sonnet: Balanced tasks, code generation
- Web Research: Finding latest best practices

This system auto-decides AND auto-applies improvements without human intervention.

Run with: python scripts/autonomous_brain.py
"""

import os
import sys
import json
import time
import logging
import requests
import subprocess
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum

# Cost tracking for budget management
try:
    from cost_tracker import (
        get_cost_aware_api, CostAwareAPI, BudgetStatus,
        QUALITY_TIERS, get_response_cache
    )
    COST_TRACKING_ENABLED = True
except ImportError:
    COST_TRACKING_ENABLED = False

# Setup
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🧠 BRAIN - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "autonomous_brain.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_env():
    """Load API keys from .env file."""
    env_paths = [
        SCRIPT_DIR / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            break


load_env()

# API Keys
KIE_API_KEY = os.environ.get("KIE_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Model configurations - Use best model for each task
class Model(Enum):
    HAIKU = "claude-3-haiku-20240307"        # Fast, cheap - for quick analysis
    SONNET = "claude-sonnet-4-20250514"       # Balanced - for code generation
    OPUS = "claude-opus-4-5-20251101"         # Best - for complex decisions


# File paths
BRAIN_STATE_FILE = SCRIPT_DIR / "brain_state.json"
IMPROVEMENTS_HISTORY = SCRIPT_DIR / "improvements_history.json"
BEST_PRACTICES_LEARNED = SCRIPT_DIR / "learned_practices.json"
BACKUP_DIR = SCRIPT_DIR / "backups"

# Configuration
CONFIG = {
    "cycle_interval_seconds": 180,      # 3 minutes between cycles
    "max_auto_improvements_per_day": 50,
    "confidence_threshold": 0.85,       # Only auto-apply if 85%+ confident
    "test_before_apply": True,
    "auto_rollback_on_failure": True,
    "web_research_interval": 3600,      # Research every hour
    "target_files": [
        "scripts/pokemon_studio_app.py",
        "scripts/prompt_validator.py",
        "scripts/auto_improvement_daemon.py",
        "scripts/code_improvement_daemon.py"
    ]
}


class AutonomousBrain:
    """Fully autonomous AI improvement system with cost awareness."""

    def __init__(self):
        self.running = True
        self.state = self.load_state()
        self.improvements_today = 0
        self.last_day = datetime.now().day
        self.last_research = None

        # Initialize cost tracking (quality-preserving mode)
        if COST_TRACKING_ENABLED:
            self.cost_api = get_cost_aware_api()
            self.cache = get_response_cache()
            logger.info("💰 Cost tracking enabled with quality preservation")
        else:
            self.cost_api = None
            self.cache = None
            logger.warning("⚠️ Cost tracking not available")

    def load_state(self) -> dict:
        """Load brain state from file."""
        if BRAIN_STATE_FILE.exists():
            try:
                with open(BRAIN_STATE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_improvements": 0,
            "successful_improvements": 0,
            "failed_improvements": 0,
            "learned_patterns": [],
            "avoid_patterns": [],
            "quality_trend": [],
            "last_research_findings": {}
        }

    def save_state(self):
        """Save brain state to file."""
        try:
            with open(BRAIN_STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    # ================================================================
    # AI MODEL CALLS (with cost tracking & quality preservation)
    # ================================================================

    def _check_budget(self, task_type: str = "general") -> Tuple[bool, Optional[str]]:
        """
        Check if we can make an API call within budget.

        Quality preservation: Critical tasks are never blocked except when budget exceeded.
        """
        if not self.cost_api:
            return True, None

        status, info = self.cost_api.tracker.get_budget_status()

        if status == BudgetStatus.EXCEEDED:
            logger.warning(f"❌ Budget exceeded! Monthly: ${info['monthly_spent_usd']:.2f}/${info['monthly_limit_usd']}")
            return False, None

        # Get recommended model (quality-preserving)
        model = self.cost_api.get_model_for_task(task_type)
        return True, model

    def call_claude(self, prompt: str, model: Model, system: str = "",
                    max_tokens: int = 4096, task_type: str = "general") -> Optional[str]:
        """
        Call Claude API with specified model.

        Features:
        - Cost tracking and budget enforcement
        - Response caching to avoid duplicate calls
        - Quality-preserving model selection
        """
        if not ANTHROPIC_API_KEY:
            logger.error("No Anthropic API key!")
            return None

        # Check budget (quality-preserving)
        if self.cost_api:
            can_call, recommended_model = self._check_budget(task_type)
            if not can_call:
                logger.warning(f"⏸️ Skipping API call due to budget constraints")
                return None

        # Check cache first (saves money!)
        cache_key = f"{model.value}:{task_type}:{prompt[:500]}"
        if self.cache:
            cached = self.cache.get(prompt[:500], model.value, task_type)
            if cached:
                logger.info(f"💾 Cache hit for {task_type}! Saved API cost")
                return cached

        try:
            payload = {
                "model": model.value,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system:
                payload["system"] = system

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result_json = response.json()
                text_response = result_json.get("content", [{}])[0].get("text", "")

                # Track cost
                if self.cost_api:
                    usage = result_json.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    cost = self.cost_api.record_call(
                        "claude", model.value, input_tokens, output_tokens, task_type
                    )
                    if cost > 0.01:
                        logger.info(f"💰 Cost: ${cost:.4f} ({model.name})")

                # Cache the response
                if self.cache and text_response:
                    self.cache.set(prompt[:500], model.value, task_type, text_response)

                return text_response
            else:
                logger.error(f"Claude API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None

    def call_haiku_fast(self, prompt: str, system: str = "", task_type: str = "quick_scan") -> Optional[str]:
        """Quick analysis with Haiku - for fast decisions."""
        return self.call_claude(prompt, Model.HAIKU, system, max_tokens=1024, task_type=task_type)

    def call_opus_expert(self, prompt: str, system: str = "", task_type: str = "final_decision") -> Optional[str]:
        """Expert analysis with Opus 4.5 - for complex decisions (quality-critical)."""
        return self.call_claude(prompt, Model.OPUS, system, max_tokens=8192, task_type=task_type)

    def call_sonnet_balanced(self, prompt: str, system: str = "", task_type: str = "code_generation") -> Optional[str]:
        """Balanced analysis with Sonnet - for code generation."""
        return self.call_claude(prompt, Model.SONNET, system, max_tokens=4096, task_type=task_type)

    # ================================================================
    # WEB RESEARCH
    # ================================================================

    def web_search(self, query: str) -> Optional[list]:
        """Search the web for best practices and latest techniques."""
        # Using a simple approach - in production you'd use a proper search API
        logger.info(f"🔍 Web research: {query}")

        # Use Claude to simulate web research based on its knowledge
        system = """You are a research assistant finding the latest best practices.
Return a JSON array of findings:
[
    {
        "topic": "topic name",
        "best_practice": "description",
        "implementation": "how to implement",
        "source": "where this is commonly used"
    }
]"""

        prompt = f"""Research the latest best practices for: {query}

Focus on:
1. Python/Streamlit best practices 2024-2025
2. AI/ML application patterns
3. Code quality and performance
4. Security best practices

Return as JSON array:"""

        result = self.call_haiku_fast(prompt, system)

        if result:
            try:
                # Parse JSON
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                return json.loads(result.strip())
            except:
                pass
        return None

    def research_best_practices(self):
        """Periodic web research for latest best practices."""
        if self.last_research and datetime.now() - self.last_research < timedelta(seconds=CONFIG["web_research_interval"]):
            return

        logger.info("🌐 Starting web research for best practices...")

        topics = [
            "Python Streamlit application architecture 2025",
            "AI image generation prompt engineering best practices",
            "Claude API integration patterns",
            "Python daemon process management"
        ]

        findings = {}
        for topic in topics:
            result = self.web_search(topic)
            if result:
                findings[topic] = result

        if findings:
            self.state["last_research_findings"] = findings
            logger.info(f"📚 Learned {len(findings)} new topics from research")

        self.last_research = datetime.now()
        self.save_state()

    # ================================================================
    # CODE ANALYSIS & IMPROVEMENT
    # ================================================================

    def read_file(self, file_path: str) -> Optional[str]:
        """Read file contents."""
        full_path = PROJECT_ROOT / file_path
        try:
            with open(full_path) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None

    def analyze_code_quick(self, file_path: str, code: str) -> dict:
        """Quick analysis with Haiku to identify issues."""
        system = """You are a code analyzer. Quickly identify the top 3 most impactful improvements.
Return JSON:
{
    "quality_score": <1-10>,
    "top_issues": [
        {"severity": "high/medium/low", "description": "...", "fix_complexity": "simple/moderate/complex"}
    ],
    "quick_wins": ["list of easy improvements"]
}"""

        # Truncate code for quick analysis
        code_sample = code[:15000] if len(code) > 15000 else code

        prompt = f"""Analyze this Python file quickly: {file_path}

```python
{code_sample}
```

Return JSON analysis:"""

        result = self.call_haiku_fast(prompt, system)

        if result:
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                return json.loads(result.strip())
            except:
                pass

        return {"quality_score": 5, "top_issues": [], "quick_wins": []}

    def decide_improvement_with_opus(self, file_path: str, code: str, issues: list) -> Optional[dict]:
        """Use Opus 4.5 to make complex improvement decisions."""
        system = """You are an expert software architect making autonomous improvement decisions.

You must decide:
1. Should this improvement be auto-applied? (only if safe and beneficial)
2. What exactly should change?
3. How confident are you? (0-1)

Return JSON:
{
    "should_auto_apply": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "why this decision",
    "improvement": {
        "description": "what we're improving",
        "category": "bug_fix/performance/security/code_quality/feature",
        "changes": [
            {
                "type": "replace",
                "original": "exact code to find",
                "new": "replacement code",
                "explanation": "why this change"
            }
        ]
    },
    "risks": ["potential risks"],
    "test_command": "command to verify"
}

Rules for auto-apply:
- Only simple, safe changes (no breaking changes)
- High confidence (>0.85)
- Clear improvement with low risk
- No changes to critical security code without review"""

        # Use first significant issue
        issue = issues[0] if issues else {"description": "general improvement needed"}

        prompt = f"""File: {file_path}

Issue to address:
{json.dumps(issue, indent=2)}

Current code (relevant section):
```python
{code[:20000]}
```

Learned patterns to apply: {self.state.get('learned_patterns', [])[:5]}
Patterns to avoid: {self.state.get('avoid_patterns', [])[:5]}

Make your improvement decision:"""

        result = self.call_opus_expert(prompt, system)

        if result:
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                return json.loads(result.strip())
            except Exception as e:
                logger.warning(f"Failed to parse Opus decision: {e}")

        return None

    def generate_code_with_sonnet(self, file_path: str, code: str, improvement: dict) -> Optional[list]:
        """Use Sonnet to generate actual code changes."""
        system = """You are an expert Python developer generating precise code changes.

Return JSON array of changes:
[
    {
        "type": "replace",
        "original": "EXACT code to find (copy-paste exactly)",
        "new": "new code to replace with",
        "line_hint": approximate_line_number
    }
]

Rules:
1. Original must be EXACT match (whitespace matters)
2. Keep changes minimal and focused
3. Preserve existing style
4. Don't break imports or dependencies"""

        prompt = f"""Generate code changes for: {file_path}

Improvement: {improvement.get('description', '')}
Category: {improvement.get('category', '')}

Current code:
```python
{code[:25000]}
```

Generate the precise code changes as JSON:"""

        result = self.call_sonnet_balanced(prompt, system)

        if result:
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                return json.loads(result.strip())
            except:
                pass

        return None

    # ================================================================
    # AUTO-APPLY CHANGES
    # ================================================================

    def backup_file(self, file_path: str) -> Optional[Path]:
        """Create backup before modification."""
        BACKUP_DIR.mkdir(exist_ok=True)
        full_path = PROJECT_ROOT / file_path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(file_path).stem}_{timestamp}.py"
        backup_path = BACKUP_DIR / backup_name

        try:
            shutil.copy(full_path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    def apply_changes(self, file_path: str, changes: list) -> Tuple[bool, str]:
        """Apply code changes to file."""
        full_path = PROJECT_ROOT / file_path

        try:
            with open(full_path) as f:
                code = f.read()

            original_hash = hashlib.md5(code.encode()).hexdigest()

            for change in changes:
                original = change.get("original", "")
                new = change.get("new", "")

                if not original:
                    continue

                if original in code:
                    code = code.replace(original, new, 1)
                    logger.info(f"✅ Applied change: {original[:50]}...")
                else:
                    logger.warning(f"⚠️ Original not found: {original[:50]}...")
                    return False, "Original code not found"

            # Verify syntax
            try:
                compile(code, file_path, 'exec')
            except SyntaxError as e:
                return False, f"Syntax error: {e}"

            # Check if actually changed
            new_hash = hashlib.md5(code.encode()).hexdigest()
            if original_hash == new_hash:
                return False, "No changes made"

            # Write changes
            with open(full_path, 'w') as f:
                f.write(code)

            return True, "Changes applied successfully"

        except Exception as e:
            return False, str(e)

    def run_tests(self) -> Tuple[bool, str]:
        """Run tests to verify changes."""
        try:
            # Test 1: Import test
            result = subprocess.run(
                [sys.executable, "-c", "import scripts.pokemon_studio_app; import scripts.prompt_validator"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return False, f"Import failed: {result.stderr[:200]}"

            # Test 2: Syntax check all target files
            for file_path in CONFIG["target_files"]:
                full_path = PROJECT_ROOT / file_path
                if full_path.exists():
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(full_path)],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode != 0:
                        return False, f"Syntax error in {file_path}"

            return True, "All tests passed"

        except subprocess.TimeoutExpired:
            return False, "Test timeout"
        except Exception as e:
            return False, str(e)

    def rollback(self, file_path: str, backup_path: Path):
        """Rollback file from backup."""
        try:
            shutil.copy(backup_path, PROJECT_ROOT / file_path)
            logger.info(f"🔄 Rolled back {file_path}")
        except Exception as e:
            logger.error(f"Rollback failed: {e}")

    def log_improvement(self, success: bool, file_path: str, improvement: dict, error: str = None):
        """Log improvement attempt to history."""
        history = []
        if IMPROVEMENTS_HISTORY.exists():
            try:
                with open(IMPROVEMENTS_HISTORY) as f:
                    history = json.load(f)
            except:
                pass

        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "success": success,
            "improvement": improvement.get("description", "unknown"),
            "category": improvement.get("category", "unknown"),
            "error": error
        }

        history.append(entry)
        history = history[-500:]  # Keep last 500

        with open(IMPROVEMENTS_HISTORY, 'w') as f:
            json.dump(history, f, indent=2)

        # Update state
        self.state["total_improvements"] += 1
        if success:
            self.state["successful_improvements"] += 1
            # Learn from success
            pattern = f"Successfully applied: {improvement.get('category', '')} - {improvement.get('description', '')[:50]}"
            if pattern not in self.state["learned_patterns"]:
                self.state["learned_patterns"].append(pattern)
                self.state["learned_patterns"] = self.state["learned_patterns"][-50:]
        else:
            self.state["failed_improvements"] += 1
            # Learn from failure
            pattern = f"Failed: {improvement.get('description', '')[:50]} - {error}"
            if pattern not in self.state["avoid_patterns"]:
                self.state["avoid_patterns"].append(pattern)
                self.state["avoid_patterns"] = self.state["avoid_patterns"][-30:]

        self.save_state()

    # ================================================================
    # MAIN IMPROVEMENT CYCLE
    # ================================================================

    def run_improvement_cycle(self):
        """Run one autonomous improvement cycle."""
        logger.info("=" * 60)
        logger.info("🧠 Starting autonomous improvement cycle")
        logger.info(f"   Using: Haiku (fast) → Opus (decisions) → Sonnet (code)")

        # Reset daily counter
        if datetime.now().day != self.last_day:
            self.improvements_today = 0
            self.last_day = datetime.now().day

        # Rate limit
        if self.improvements_today >= CONFIG["max_auto_improvements_per_day"]:
            logger.info("Daily improvement limit reached")
            return

        # Periodic web research
        self.research_best_practices()

        # Process each target file
        for file_path in CONFIG["target_files"]:
            logger.info(f"\n📂 Processing: {file_path}")

            code = self.read_file(file_path)
            if not code:
                continue

            # Step 1: Quick analysis with Haiku
            logger.info("   🐇 Quick analysis with Haiku...")
            analysis = self.analyze_code_quick(file_path, code)
            quality = analysis.get("quality_score", 5)
            issues = analysis.get("top_issues", [])

            logger.info(f"   Quality: {quality}/10, Issues: {len(issues)}")

            if not issues:
                logger.info("   ✨ No issues found!")
                continue

            # Step 2: Expert decision with Opus 4.5
            logger.info("   🦉 Expert decision with Opus 4.5...")
            decision = self.decide_improvement_with_opus(file_path, code, issues)

            if not decision:
                logger.info("   ⏭️ No improvement decision made")
                continue

            confidence = decision.get("confidence", 0)
            should_apply = decision.get("should_auto_apply", False)

            logger.info(f"   Confidence: {confidence:.0%}")
            logger.info(f"   Auto-apply: {should_apply}")
            logger.info(f"   Reasoning: {decision.get('reasoning', 'N/A')[:100]}")

            # Check if we should auto-apply
            if not should_apply or confidence < CONFIG["confidence_threshold"]:
                logger.info(f"   ⏸️ Skipping (confidence too low or not safe)")
                continue

            improvement = decision.get("improvement", {})
            changes = improvement.get("changes", [])

            # Step 3: Generate precise code with Sonnet if needed
            if not changes:
                logger.info("   ✍️ Generating code with Sonnet...")
                changes = self.generate_code_with_sonnet(file_path, code, improvement)

            if not changes:
                logger.info("   ❌ Could not generate code changes")
                continue

            # Step 4: Apply changes with backup
            logger.info(f"   🔧 Applying {len(changes)} changes...")

            backup = self.backup_file(file_path)
            if not backup:
                logger.error("   ❌ Backup failed, aborting")
                continue

            success, message = self.apply_changes(file_path, changes)

            if not success:
                logger.warning(f"   ❌ Apply failed: {message}")
                self.log_improvement(False, file_path, improvement, message)
                continue

            # Step 5: Run tests
            if CONFIG["test_before_apply"]:
                logger.info("   🧪 Running tests...")
                test_pass, test_msg = self.run_tests()

                if not test_pass:
                    logger.warning(f"   ❌ Tests failed: {test_msg}")
                    if CONFIG["auto_rollback_on_failure"]:
                        self.rollback(file_path, backup)
                    self.log_improvement(False, file_path, improvement, test_msg)
                    continue

            # Success!
            logger.info(f"   ✅ Successfully applied: {improvement.get('description', 'improvement')[:50]}")
            self.log_improvement(True, file_path, improvement)
            self.improvements_today += 1

            # Track quality trend
            self.state["quality_trend"].append({
                "timestamp": datetime.now().isoformat(),
                "file": file_path,
                "before": quality,
                "improvement": improvement.get("description", "")[:50]
            })
            self.state["quality_trend"] = self.state["quality_trend"][-100:]

        self.save_state()
        logger.info("\n🧠 Improvement cycle completed")
        logger.info(f"   Today's improvements: {self.improvements_today}")
        logger.info(f"   Total successful: {self.state['successful_improvements']}")
        logger.info("=" * 60)

    def run(self):
        """Main daemon loop."""
        logger.info("=" * 60)
        logger.info("🧠 AUTONOMOUS BRAIN STARTING")
        logger.info("=" * 60)
        logger.info(f"Models: Haiku (fast) | Sonnet (code) | Opus 4.5 (decisions)")
        logger.info(f"Anthropic API: {'✅ Found' if ANTHROPIC_API_KEY else '❌ Missing'}")
        logger.info(f"Confidence threshold: {CONFIG['confidence_threshold']:.0%}")
        logger.info(f"Cycle interval: {CONFIG['cycle_interval_seconds']}s")
        logger.info("=" * 60)

        if not ANTHROPIC_API_KEY:
            logger.error("Missing Anthropic API key!")
            return

        while self.running:
            try:
                self.run_improvement_cycle()
            except KeyboardInterrupt:
                logger.info("Shutdown requested...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Cycle error: {e}")
                import traceback
                traceback.print_exc()

            if self.running:
                logger.info(f"💤 Sleeping {CONFIG['cycle_interval_seconds']}s...")
                time.sleep(CONFIG["cycle_interval_seconds"])

        logger.info("🧠 Brain stopped")
        self.save_state()


def print_status():
    """Print brain status."""
    print("\n" + "=" * 60)
    print("  🧠 Autonomous Brain - Status")
    print("=" * 60)

    # Cost tracking status
    if COST_TRACKING_ENABLED:
        try:
            cost_api = get_cost_aware_api()
            summary = cost_api.get_cost_summary()
            print(f"\n💰 Budget Status: {summary['status'].upper()}")
            print(f"   Daily: ${summary['daily_spent_usd']:.4f} / ${summary['daily_limit_usd']:.2f} ({summary['daily_percent']}%)")
            print(f"   Monthly: ${summary['monthly_spent_usd']:.4f} / ${summary['monthly_limit_usd']:.2f} ({summary['monthly_percent']}%)")
            print(f"   Monthly (INR): ₹{summary['monthly_spent_inr']:.0f}")
            if summary.get('cache_entries', 0) > 0:
                print(f"   Cache entries: {summary['cache_entries']} (saves repeat calls)")
            if summary['quality_preservation_enabled']:
                print(f"   🛡️ Quality preservation: ENABLED")
        except Exception as e:
            print(f"\n💰 Cost tracking error: {e}")
    else:
        print("\n⚠️ Cost tracking not enabled")

    if BRAIN_STATE_FILE.exists():
        with open(BRAIN_STATE_FILE) as f:
            state = json.load(f)

        total = state.get("total_improvements", 0)
        success = state.get("successful_improvements", 0)
        failed = state.get("failed_improvements", 0)
        rate = (success / total * 100) if total > 0 else 0

        print(f"\n📊 Improvement Statistics:")
        print(f"   Total improvements: {total}")
        print(f"   Successful: {success} ({rate:.1f}%)")
        print(f"   Failed: {failed}")

        patterns = state.get("learned_patterns", [])
        if patterns:
            print(f"\n📚 Learned patterns ({len(patterns)}):")
            for p in patterns[-5:]:
                print(f"   • {p[:60]}")

        avoid = state.get("avoid_patterns", [])
        if avoid:
            print(f"\n⚠️ Patterns to avoid ({len(avoid)}):")
            for p in avoid[-3:]:
                print(f"   • {p[:60]}")

        trend = state.get("quality_trend", [])
        if trend:
            print(f"\n📈 Recent improvements:")
            for t in trend[-5:]:
                print(f"   • {t.get('file', 'unknown')}: {t.get('improvement', '')[:40]}")

    else:
        print("\nNo brain state found. Run the brain first.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pokemon AI Autonomous Brain")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--once", action="store_true", help="Run single cycle")
    args = parser.parse_args()

    if args.status:
        print_status()
    elif args.once:
        brain = AutonomousBrain()
        brain.run_improvement_cycle()
    else:
        brain = AutonomousBrain()
        brain.run()
