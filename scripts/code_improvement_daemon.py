#!/usr/bin/env python3
"""
Pokemon AI Video Generator - Code Auto-Improvement Daemon

This daemon uses Claude API to continuously analyze and improve
the codebase itself - adding features, fixing bugs, refactoring,
and optimizing code quality.

Features:
- Analyzes code quality and identifies improvements
- Generates code improvements using Claude API
- Tests changes before applying
- Creates feature suggestions based on usage patterns
- Maintains improvement history and rollback capability

Run with: python scripts/code_improvement_daemon.py
"""

import os
import sys
import json
import time
import logging
import requests
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "code_improvement.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_env():
    """Load API keys from .env file."""
    env_paths = [
        Path(__file__).parent / ".env",
        Path.cwd() / ".env",
        Path.cwd() / "scripts" / ".env"
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            logger.info(f"Loaded env from {env_path}")
            break


load_env()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

@dataclass
class DaemonConfig:
    """Configuration for the code improvement daemon."""
    check_interval_seconds: int = 600  # 10 minutes between improvement cycles
    max_improvements_per_day: int = 20
    backup_before_changes: bool = True
    auto_apply_safe_changes: bool = False  # Set to True for fully autonomous
    require_test_pass: bool = True
    target_files: list = field(default_factory=lambda: [
        "scripts/pokemon_studio_app.py",
        "scripts/prompt_validator.py",
        "scripts/auto_improvement_daemon.py"
    ])
    improvement_categories: list = field(default_factory=lambda: [
        "bug_fix",
        "performance",
        "code_quality",
        "new_feature",
        "ui_improvement",
        "documentation"
    ])


# Default configuration instance
CONFIG = DaemonConfig()

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
IMPROVEMENTS_FILE = Path(__file__).parent / "code_improvements.json"
SUGGESTIONS_FILE = Path(__file__).parent / "feature_suggestions.json"
BACKUP_DIR = Path(__file__).parent / "backups"


class CodeImprovementDaemon:
    """Daemon for autonomous code improvement using Claude API."""

    def __init__(self, config: Optional[DaemonConfig] = None, api_key: Optional[str] = None):
        self.config = config or CONFIG
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.running = True
        self.improvements_today = 0
        self.last_day_reset = datetime.now().day
        self.improvements = self.load_improvements()
        self.suggestions = self.load_suggestions()

    def load_improvements(self) -> dict:
        """Load previous improvements from file."""
        if IMPROVEMENTS_FILE.exists():
            try:
                with open(IMPROVEMENTS_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading improvements: {e}")
        return {
            "applied": [],
            "pending": [],
            "rejected": [],
            "quality_scores": {}
        }

    def save_improvements(self):
        """Save improvements to file."""
        try:
            with open(IMPROVEMENTS_FILE, 'w') as f:
                json.dump(self.improvements, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving improvements: {e}")

    def load_suggestions(self) -> list:
        """Load feature suggestions."""
        if SUGGESTIONS_FILE.exists():
            try:
                with open(SUGGESTIONS_FILE) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError) as e:
                logger.warning(f"Error loading suggestions file: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading suggestions: {e}")
        return []

    def save_suggestions(self):
        """Save feature suggestions."""
        try:
            with open(SUGGESTIONS_FILE, 'w') as f:
                json.dump(self.suggestions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving suggestions: {e}")

    def backup_file(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a file before modification."""
        if not self.config.backup_before_changes:
            return None

        BACKUP_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = BACKUP_DIR / backup_name

        try:
            shutil.copy(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    def read_file(self, file_path: str) -> Optional[str]:
        """Read file contents."""
        full_path = PROJECT_ROOT / file_path
        try:
            with open(full_path) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None

    def analyze_code_with_claude(self, file_path: str, code: str) -> dict:
        """Analyze code quality and identify improvements using Claude."""
        if not self.api_key:
            return {"error": "No API key"}

        system_prompt = """You are an expert Python code reviewer and software architect.
Analyze the provided code and identify potential improvements.

Return a JSON object with:
{
    "quality_score": <1-10>,
    "issues": [
        {
            "type": "bug|performance|style|security|maintainability",
            "severity": "low|medium|high|critical",
            "line_range": [start, end],
            "description": "description of the issue",
            "suggested_fix": "how to fix it"
        }
    ],
    "improvements": [
        {
            "category": "bug_fix|performance|code_quality|new_feature|ui_improvement",
            "priority": "low|medium|high",
            "description": "what to improve",
            "implementation_hint": "how to implement"
        }
    ],
    "feature_suggestions": [
        {
            "name": "feature name",
            "description": "what it does",
            "complexity": "low|medium|high",
            "value": "low|medium|high"
        }
    ],
    "overall_assessment": "brief summary"
}

Focus on:
1. Bug risks and edge cases
2. Performance bottlenecks
3. Code maintainability
4. Security issues
5. UX improvements for Streamlit app
6. Missing error handling
7. Potential new features"""

        # Truncate code if too long (keep first and last parts)
        max_chars = 50000
        if len(code) > max_chars:
            half = max_chars // 2
            code = code[:half] + "\n\n... [TRUNCATED] ...\n\n" + code[-half:]

        user_message = f"""Analyze this Python file: {file_path}

```python
{code}
```

Provide your analysis as JSON:"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": user_message}],
                    "system": system_prompt
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("content", [{}])[0].get("text", "")

                # Parse JSON
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]

                try:
                    return json.loads(text.strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse analysis as JSON")
                    return {"error": "JSON parse error", "raw": text[:500]}
            else:
                return {"error": f"API error {response.status_code}"}

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"error": str(e)}

    def generate_code_improvement(self, file_path: str, code: str, improvement: dict) -> Optional[dict]:
        """Generate specific code improvement using Claude."""
        if not ANTHROPIC_API_KEY:
            return None

        system_prompt = """You are an expert Python developer.
Generate a specific code improvement based on the provided suggestion.

Return a JSON object with:
{
    "description": "what this change does",
    "changes": [
        {
            "type": "replace|insert|delete",
            "original": "original code snippet (exact match)",
            "new": "new code to replace with",
            "explanation": "why this change"
        }
    ],
    "test_suggestion": "how to verify this change works",
    "risk_level": "low|medium|high",
    "rollback_notes": "how to undo if needed"
}

Rules:
1. Make minimal, targeted changes
2. Preserve existing functionality
3. Don't break imports or dependencies
4. Use exact string matches for original code
5. Test carefully"""

        user_message = f"""File: {file_path}

Improvement to implement:
- Category: {improvement.get('category', 'unknown')}
- Description: {improvement.get('description', '')}
- Hint: {improvement.get('implementation_hint', '')}

Current code:
```python
{code[:30000]}
```

Generate the code changes as JSON:"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": user_message}],
                    "system": system_prompt
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("content", [{}])[0].get("text", "")

                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]

                try:
                    return json.loads(text.strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse code changes as JSON")
                    return None
            else:
                logger.error(f"Code generation API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return None

    def apply_changes(self, file_path: str, changes: list) -> bool:
        """Apply code changes to a file."""
        full_path = PROJECT_ROOT / file_path

        try:
            with open(full_path) as f:
                code = f.read()

            original_code = code

            for change in changes:
                change_type = change.get("type", "replace")
                original = change.get("original", "")
                new = change.get("new", "")

                if change_type == "replace" and original:
                    if original in code:
                        code = code.replace(original, new, 1)
                        logger.info(f"Applied replacement: {original[:50]}... -> {new[:50]}...")
                    else:
                        logger.warning(f"Original code not found: {original[:100]}...")
                        return False

                elif change_type == "insert":
                    # Insert after original
                    if original in code:
                        code = code.replace(original, original + new, 1)
                    else:
                        logger.warning(f"Insert anchor not found: {original[:100]}...")
                        return False

                elif change_type == "delete" and original:
                    code = code.replace(original, "", 1)

            # Verify syntax
            try:
                compile(code, file_path, 'exec')
            except SyntaxError as e:
                logger.error(f"Syntax error in modified code: {e}")
                return False

            # Write changes
            with open(full_path, 'w') as f:
                f.write(code)

            logger.info(f"Changes applied to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error applying changes: {e}")
            return False

    def run_tests(self) -> bool:
        """Run tests to verify changes."""
        try:
            # Try to run any existing tests
            result = subprocess.run(
                ["python", "-c", "import scripts.pokemon_studio_app"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("Import test passed")
                return True
            else:
                logger.error(f"Import test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("Test timeout")
            return False
        except Exception as e:
            logger.error(f"Test error: {e}")
            return False

    def rollback_file(self, file_path: str, backup_path: Path):
        """Rollback a file from backup."""
        full_path = PROJECT_ROOT / file_path
        try:
            shutil.copy(backup_path, full_path)
            logger.info(f"Rolled back {file_path} from {backup_path}")
        except Exception as e:
            logger.error(f"Rollback failed: {e}")


    def _process_improvement(self, file_path: str, code: str, improvement: dict) -> bool:
        """Process a single improvement and return True if applied."""
        logger.info(f"\nImprovement: {improvement.get('description', '')[:100]}")

        code_changes = self.generate_code_improvement(file_path, code, improvement)
        if not code_changes or not code_changes.get("changes"):
            return False

        risk = code_changes.get("risk_level", "high")
        logger.info(f"Risk level: {risk}")

        pending_item = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "improvement": improvement,
            "changes": code_changes,
            "status": "pending"
        }

        should_auto_apply = self.config.auto_apply_safe_changes and risk == "low"
        if not should_auto_apply:
            self.improvements["pending"].append(pending_item)
            logger.info("Stored for manual review")
            return False

        logger.info("Auto-applying low-risk change...")
        backup = self.backup_file(PROJECT_ROOT / file_path)

        if not self.apply_changes(file_path, code_changes["changes"]):
            return False

        if self.config.require_test_pass and not self.run_tests():
            logger.warning("Tests failed! Rolling back...")
            if backup:
                self.rollback_file(file_path, backup)
            pending_item["status"] = "rejected"
            pending_item["reason"] = "tests_failed"
            self.improvements["rejected"].append(pending_item)
            return False

        logger.info("Change applied successfully!")
        pending_item["status"] = "applied"
        self.improvements["applied"].append(pending_item)
        return True


        """Run one code improvement cycle."""
        logger.info("=" * 60)
        logger.info("Starting code improvement cycle")

        # Rate limiting
        current_day = datetime.now().day
        if current_day != self.last_day_reset:
            self.improvements_today = 0
            self.last_day_reset = current_day

        if self.improvements_today >= CONFIG["max_improvements_per_day"]:
            logger.info("Daily improvement limit reached. Waiting...")
            return

        # Analyze each target file
        for file_path in CONFIG["target_files"]:
            logger.info(f"\nAnalyzing: {file_path}")

            code = self.read_file(file_path)
            if not code:
                continue

            # Get analysis from Claude
            analysis = self.analyze_code_with_claude(file_path, code)

            if "error" in analysis:
                logger.error(f"Analysis failed: {analysis.get('error')}")
                continue

            quality_score = analysis.get("quality_score", 0)
            logger.info(f"Quality score: {quality_score}/10")

            # Store quality score history
            if file_path not in self.improvements["quality_scores"]:
                self.improvements["quality_scores"][file_path] = []
            self.improvements["quality_scores"][file_path].append({
                "timestamp": datetime.now().isoformat(),
                "score": quality_score
            })

            # Process issues
            issues = analysis.get("issues", [])
            if issues:
                logger.info(f"Found {len(issues)} issues:")
                for issue in issues[:3]:
                    logger.info(f"  - [{issue.get('severity', 'unknown')}] {issue.get('description', '')[:80]}")

            # Process improvement suggestions
            improvements = analysis.get("improvements", [])
            high_priority = [i for i in improvements if i.get("priority") == "high"]

            if not high_priority or self.improvements_today >= CONFIG["max_improvements_per_day"]:
                continue

            logger.info(f"\nProcessing {len(high_priority)} high-priority improvements")

            for improvement in high_priority[:2]:  # Process max 2 per file
                if self._process_improvement(file_path, code, improvement):
                    self.improvements_today += 1

            # Store feature suggestions
            feature_suggestions = analysis.get("feature_suggestions", [])
            for suggestion in feature_suggestions:
                if suggestion not in self.suggestions:
                    suggestion["timestamp"] = datetime.now().isoformat()
                    suggestion["source_file"] = file_path
                    self.suggestions.append(suggestion)

        # Save all data
        self.save_improvements()
        self.save_suggestions()

        logger.info("\nCode improvement cycle completed")
        logger.info("=" * 60)

    def run(self):
        """Main daemon loop."""
        logger.info("=" * 60)
        logger.info("Pokemon AI Code Improvement Daemon Starting")
        logger.info(f"Anthropic API Key: {'Found' if ANTHROPIC_API_KEY else 'Missing'}")
        logger.info(f"Check interval: {CONFIG['check_interval_seconds']} seconds")
        logger.info(f"Auto-apply safe changes: {CONFIG['auto_apply_safe_changes']}")
        logger.info("=" * 60)

        if not ANTHROPIC_API_KEY:
            logger.error("Missing Anthropic API key! Cannot start daemon.")
            return

        while self.running:
            try:
                self.run_improvement_cycle()
            except KeyboardInterrupt:
                logger.info("Shutdown requested...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                import traceback
                traceback.print_exc()

            if self.running:
                logger.info(f"Sleeping for {CONFIG['check_interval_seconds']} seconds...")
                time.sleep(CONFIG["check_interval_seconds"])

        logger.info("Daemon stopped")


def print_status():
    """Print daemon status."""
    print("\n" + "=" * 60)
    print("Pokemon AI Code Improvement Daemon - Status")
    print("=" * 60)

    if IMPROVEMENTS_FILE.exists():
        with open(IMPROVEMENTS_FILE) as f:
            data = json.load(f)

        print(f"\nApplied improvements: {len(data.get('applied', []))}")
        print(f"Pending review: {len(data.get('pending', []))}")
        print(f"Rejected: {len(data.get('rejected', []))}")

        # Quality scores
        scores = data.get("quality_scores", {})
        if scores:
            print("\nLatest quality scores:")
            for file, history in scores.items():
                if history:
                    latest = history[-1]
                    print(f"  {file}: {latest.get('score', 'N/A')}/10")

        # Pending items
        pending = data.get("pending", [])
        if pending:
            print("\nPending improvements (awaiting review):")
            for item in pending[-5:]:
                print(f"  - [{item.get('file', 'unknown')}] {item.get('improvement', {}).get('description', '')[:60]}")

    if SUGGESTIONS_FILE.exists():
        with open(SUGGESTIONS_FILE) as f:
            suggestions = json.load(f)
        if suggestions:
            print(f"\nFeature suggestions: {len(suggestions)}")
            for s in suggestions[-3:]:
                print(f"  - {s.get('name', 'Unknown')}: {s.get('description', '')[:50]}")

    print("\n" + "=" * 60)


def apply_pending():
    """Interactively apply pending improvements."""
    if not IMPROVEMENTS_FILE.exists():
        print("No improvements file found.")
        return

    with open(IMPROVEMENTS_FILE) as f:
        data = json.load(f)

    pending = data.get("pending", [])
    if not pending:
        print("No pending improvements.")
        return

    print(f"\n{len(pending)} pending improvements:\n")

    for i, item in enumerate(pending):
        print(f"\n[{i+1}] File: {item.get('file')}")
        print(f"    Description: {item.get('improvement', {}).get('description', '')[:100]}")
        print(f"    Risk: {item.get('changes', {}).get('risk_level', 'unknown')}")

        response = input("    Apply? (y/n/s=skip all): ").strip().lower()

        if response == 's':
            break
        elif response == 'y':
            daemon = CodeImprovementDaemon()
            file_path = item.get("file")
            changes = item.get("changes", {}).get("changes", [])

            backup = daemon.backup_file(PROJECT_ROOT / file_path)

            if daemon.apply_changes(file_path, changes):
                if daemon.run_tests():
                    print("    ✅ Applied successfully!")
                    item["status"] = "applied"
                    data["applied"].append(item)
                else:
                    print("    ❌ Tests failed, rolling back...")
                    if backup:
                        daemon.rollback_file(file_path, backup)
                    item["status"] = "rejected"
                    item["reason"] = "tests_failed"
                    data["rejected"].append(item)
            else:
                print("    ❌ Failed to apply changes")
                item["status"] = "rejected"
                item["reason"] = "apply_failed"
                data["rejected"].append(item)

            pending.remove(item)

    data["pending"] = pending
    with open(IMPROVEMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pokemon AI Code Improvement Daemon")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--once", action="store_true", help="Run single cycle")
    parser.add_argument("--apply", action="store_true", help="Apply pending improvements")
    args = parser.parse_args()

    if args.status:
        print_status()
    elif args.apply:
        apply_pending()
    elif args.once:
        daemon = CodeImprovementDaemon()
        daemon.run_improvement_cycle()
    else:
        daemon = CodeImprovementDaemon()
        daemon.run()
