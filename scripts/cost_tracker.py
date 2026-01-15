#!/usr/bin/env python3
"""
Cost Tracker & Budget Manager

Tracks API costs and enforces budget limits to keep monthly costs
within ₹10,000-15,000 (~$120-180 USD).

Features:
- Real-time cost tracking for all API calls
- Daily and monthly budget limits
- Automatic model switching when budget is low
- Free/local alternatives for expensive operations
- Cost reports and alerts

Pricing (as of 2025):
- Claude Haiku: $0.25/M input, $1.25/M output
- Claude Sonnet: $3/M input, $15/M output
- Claude Opus 4.5: $15/M input, $75/M output
- KIE API: ~$0.01-0.05 per image/video task

Monthly Budget: ₹15,000 = ~$180 USD
Daily Budget: $6/day (with buffer)
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple, List, Any
from enum import Enum
from dataclasses import dataclass, asdict
import threading

# Setup
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 💰 COST - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cost tracking file
COST_FILE = SCRIPT_DIR / "cost_tracking.json"

# ============================================================
# PRICING CONFIGURATION (USD)
# ============================================================

# Claude API Pricing per 1M tokens
CLAUDE_PRICING = {
    "claude-3-haiku-20240307": {
        "input": 0.25,      # $0.25 per 1M input tokens
        "output": 1.25,     # $1.25 per 1M output tokens
        "name": "Haiku"
    },
    "claude-sonnet-4-20250514": {
        "input": 3.0,       # $3 per 1M input tokens
        "output": 15.0,     # $15 per 1M output tokens
        "name": "Sonnet"
    },
    "claude-opus-4-5-20251101": {
        "input": 15.0,      # $15 per 1M input tokens
        "output": 75.0,     # $75 per 1M output tokens
        "name": "Opus"
    }
}

# KIE API Pricing (estimated)
KIE_PRICING = {
    "nano-banana-pro": 0.02,          # $0.02 per image
    "kling-2.6/image-to-video": 0.05, # $0.05 per video
    "elevenlabs/text-to-speech": 0.01 # $0.01 per audio
}

# Budget Configuration
BUDGET_CONFIG = {
    "monthly_limit_usd": 180.0,      # ₹15,000 ≈ $180
    "daily_limit_usd": 6.0,          # $6/day with buffer
    "warning_threshold": 0.8,         # Warn at 80% usage
    "critical_threshold": 0.95,       # Switch to cheap mode at 95%
    "exchange_rate_inr_usd": 83.0    # 1 USD = ₹83 (approximate)
}

# ============================================================
# QUALITY PRESERVATION CONFIG
# ============================================================
# Critical tasks that ALWAYS need quality models (never downgrade)
QUALITY_CRITICAL_TASKS = {
    "final_decision",       # Opus for final go/no-go decisions
    "security_analysis",    # Can't compromise on security
    "code_review",          # Need thorough review for code quality
    "architecture_design",  # Important design decisions
}

# Tasks where quality degradation is acceptable to save costs
QUALITY_FLEXIBLE_TASKS = {
    "quick_scan",           # Initial file scanning
    "format_check",         # Formatting validation
    "simple_classification", # Basic categorization
    "summary_generation",   # Summaries (Haiku is good enough)
}

# Quality tiers: what model minimum is required for each task type
QUALITY_TIERS = {
    "critical": {           # Must use best available
        "min_model": "claude-opus-4-5-20251101",
        "fallback": "claude-sonnet-4-20250514",  # Sonnet minimum
        "tasks": ["final_decision", "security_analysis", "architecture_design"]
    },
    "high": {               # Prefer good models
        "min_model": "claude-sonnet-4-20250514",
        "fallback": "claude-sonnet-4-20250514",  # Sonnet minimum
        "tasks": ["code_generation", "code_review", "complex_analysis"]
    },
    "standard": {           # Balanced cost/quality
        "min_model": "claude-sonnet-4-20250514",
        "fallback": "claude-3-haiku-20240307",   # Can fall back to Haiku
        "tasks": ["image_analysis", "prompt_improvement", "general"]
    },
    "basic": {              # Haiku is fine
        "min_model": "claude-3-haiku-20240307",
        "fallback": "claude-3-haiku-20240307",
        "tasks": ["quick_scan", "format_check", "simple_classification", "summary"]
    }
}

# Cache configuration
CACHE_CONFIG = {
    "enabled": True,
    "max_entries": 500,
    "ttl_seconds": 3600,    # 1 hour cache TTL
    "cache_file": SCRIPT_DIR / "api_cache.json"
}


class BudgetStatus(Enum):
    """Budget status levels."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


@dataclass
class APICall:
    """Record of an API call."""
    timestamp: str
    api: str           # "claude", "kie", etc.
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    operation: str     # What was this call for


# ============================================================
# RESPONSE CACHE (Save costs by avoiding duplicate calls)
# ============================================================

class ResponseCache:
    """Cache API responses to avoid redundant calls."""

    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if CACHE_CONFIG["cache_file"].exists():
            try:
                with open(CACHE_CONFIG["cache_file"]) as f:
                    data = json.load(f)
                    # Only load non-expired entries
                    now = datetime.now().timestamp()
                    self._cache = {
                        k: v for k, v in data.items()
                        if v.get("expires", 0) > now
                    }
            except Exception:
                self._cache = {}

    def _save_cache(self):
        """Save cache to disk (async-safe)."""
        try:
            # Keep only recent entries
            if len(self._cache) > CACHE_CONFIG["max_entries"]:
                # Sort by access time and keep newest
                sorted_items = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].get("accessed", 0),
                    reverse=True
                )
                self._cache = dict(sorted_items[:CACHE_CONFIG["max_entries"]])

            with open(CACHE_CONFIG["cache_file"], 'w') as f:
                json.dump(self._cache, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _make_key(self, prompt: str, model: str, task_type: str) -> str:
        """Create cache key from prompt."""
        content = f"{model}:{task_type}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, model: str, task_type: str) -> Optional[str]:
        """Get cached response if available."""
        if not CACHE_CONFIG["enabled"]:
            return None

        key = self._make_key(prompt, model, task_type)

        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.get("expires", 0) > datetime.now().timestamp():
                    entry["accessed"] = datetime.now().timestamp()
                    logger.info(f"💾 Cache hit! Saved API call for {task_type}")
                    return entry.get("response")
                else:
                    del self._cache[key]

        return None

    def set(self, prompt: str, model: str, task_type: str, response: str):
        """Cache a response."""
        if not CACHE_CONFIG["enabled"]:
            return

        key = self._make_key(prompt, model, task_type)

        with self._lock:
            self._cache[key] = {
                "response": response,
                "model": model,
                "task_type": task_type,
                "created": datetime.now().timestamp(),
                "accessed": datetime.now().timestamp(),
                "expires": datetime.now().timestamp() + CACHE_CONFIG["ttl_seconds"]
            }
            self._save_cache()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "max_entries": CACHE_CONFIG["max_entries"],
            "enabled": CACHE_CONFIG["enabled"]
        }

    def clear(self):
        """Clear the cache."""
        with self._lock:
            self._cache = {}
            if CACHE_CONFIG["cache_file"].exists():
                CACHE_CONFIG["cache_file"].unlink()


# Global cache instance
_response_cache = None

def get_response_cache() -> ResponseCache:
    """Get global response cache."""
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache()
    return _response_cache


class CostTracker:
    """Tracks and manages API costs."""

    def __init__(self):
        self.data = self.load_data()
        self._ensure_current_period()

    def load_data(self) -> dict:
        """Load cost tracking data."""
        if COST_FILE.exists():
            try:
                with open(COST_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cost data: {e}")

        return {
            "total_spent_usd": 0.0,
            "current_month": datetime.now().strftime("%Y-%m"),
            "current_day": datetime.now().strftime("%Y-%m-%d"),
            "monthly_spent_usd": 0.0,
            "daily_spent_usd": 0.0,
            "calls": [],
            "daily_breakdown": {},
            "monthly_breakdown": {}
        }

    def save_data(self):
        """Save cost tracking data."""
        try:
            with open(COST_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cost data: {e}")

    def _ensure_current_period(self):
        """Reset counters for new day/month if needed."""
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")

        # Reset daily counter
        if self.data["current_day"] != today:
            self.data["current_day"] = today
            self.data["daily_spent_usd"] = 0.0

        # Reset monthly counter
        if self.data["current_month"] != this_month:
            self.data["current_month"] = this_month
            self.data["monthly_spent_usd"] = 0.0

    def calculate_claude_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a Claude API call."""
        if model not in CLAUDE_PRICING:
            logger.warning(f"Unknown model: {model}, using Sonnet pricing")
            model = "claude-sonnet-4-20250514"

        pricing = CLAUDE_PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def calculate_kie_cost(self, model: str) -> float:
        """Calculate cost for a KIE API call."""
        return KIE_PRICING.get(model, 0.03)  # Default to $0.03

    def record_claude_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str = "unknown"
    ) -> float:
        """Record a Claude API call and return cost."""
        self._ensure_current_period()

        cost = self.calculate_claude_cost(model, input_tokens, output_tokens)

        call = APICall(
            timestamp=datetime.now().isoformat(),
            api="claude",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            operation=operation
        )

        self._record_call(call)
        return cost

    def record_kie_call(self, model: str, operation: str = "unknown") -> float:
        """Record a KIE API call and return cost."""
        self._ensure_current_period()

        cost = self.calculate_kie_cost(model)

        call = APICall(
            timestamp=datetime.now().isoformat(),
            api="kie",
            model=model,
            input_tokens=0,
            output_tokens=0,
            cost_usd=cost,
            operation=operation
        )

        self._record_call(call)
        return cost

    def _record_call(self, call: APICall):
        """Record an API call."""
        self.data["total_spent_usd"] += call.cost_usd
        self.data["monthly_spent_usd"] += call.cost_usd
        self.data["daily_spent_usd"] += call.cost_usd

        # Keep last 1000 calls
        self.data["calls"].append(asdict(call))
        self.data["calls"] = self.data["calls"][-1000:]

        # Update breakdowns
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")

        if today not in self.data["daily_breakdown"]:
            self.data["daily_breakdown"][today] = 0.0
        self.data["daily_breakdown"][today] += call.cost_usd

        if this_month not in self.data["monthly_breakdown"]:
            self.data["monthly_breakdown"][this_month] = 0.0
        self.data["monthly_breakdown"][this_month] += call.cost_usd

        self.save_data()

        # Log significant costs
        if call.cost_usd > 0.01:
            logger.info(f"💰 {call.api}/{call.model}: ${call.cost_usd:.4f} ({call.operation})")

    def get_budget_status(self) -> Tuple[BudgetStatus, dict]:
        """Get current budget status."""
        self._ensure_current_period()

        daily_pct = self.data["daily_spent_usd"] / BUDGET_CONFIG["daily_limit_usd"]
        monthly_pct = self.data["monthly_spent_usd"] / BUDGET_CONFIG["monthly_limit_usd"]

        # Determine status based on monthly usage
        if monthly_pct >= 1.0:
            status = BudgetStatus.EXCEEDED
        elif monthly_pct >= BUDGET_CONFIG["critical_threshold"]:
            status = BudgetStatus.CRITICAL
        elif monthly_pct >= BUDGET_CONFIG["warning_threshold"]:
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.OK

        info = {
            "status": status.value,
            "daily_spent_usd": round(self.data["daily_spent_usd"], 4),
            "daily_limit_usd": BUDGET_CONFIG["daily_limit_usd"],
            "daily_remaining_usd": round(BUDGET_CONFIG["daily_limit_usd"] - self.data["daily_spent_usd"], 4),
            "daily_percent": round(daily_pct * 100, 1),
            "monthly_spent_usd": round(self.data["monthly_spent_usd"], 4),
            "monthly_limit_usd": BUDGET_CONFIG["monthly_limit_usd"],
            "monthly_remaining_usd": round(BUDGET_CONFIG["monthly_limit_usd"] - self.data["monthly_spent_usd"], 4),
            "monthly_percent": round(monthly_pct * 100, 1),
            "monthly_spent_inr": round(self.data["monthly_spent_usd"] * BUDGET_CONFIG["exchange_rate_inr_usd"], 0)
        }

        return status, info

    def can_afford(self, estimated_cost_usd: float) -> bool:
        """Check if we can afford an operation."""
        status, info = self.get_budget_status()

        if status == BudgetStatus.EXCEEDED:
            return False

        # Check if this would exceed daily limit
        if self.data["daily_spent_usd"] + estimated_cost_usd > BUDGET_CONFIG["daily_limit_usd"]:
            logger.warning(f"Daily budget would be exceeded by ${estimated_cost_usd:.4f}")
            return False

        # Check if this would exceed monthly limit
        if self.data["monthly_spent_usd"] + estimated_cost_usd > BUDGET_CONFIG["monthly_limit_usd"]:
            logger.warning(f"Monthly budget would be exceeded by ${estimated_cost_usd:.4f}")
            return False

        return True

    def get_recommended_model(self, task_type: str = "general", preserve_quality: bool = True) -> str:
        """
        Get recommended model based on budget status AND quality requirements.

        QUALITY PRESERVATION: Critical tasks never get downgraded, even when budget is tight.
        This ensures quality doesn't degrade significantly while still saving costs on flexible tasks.

        Args:
            task_type: Type of task to perform
            preserve_quality: If True, never downgrade critical tasks

        Returns:
            Recommended model ID, or None if budget exceeded
        """
        status, info = self.get_budget_status()

        # Find which quality tier this task belongs to
        task_tier = "standard"  # default
        for tier_name, tier_config in QUALITY_TIERS.items():
            if task_type in tier_config["tasks"]:
                task_tier = tier_name
                break

        tier_config = QUALITY_TIERS[task_tier]

        # QUALITY PRESERVATION LOGIC
        # Critical/high quality tasks get minimum quality even when budget is tight
        if preserve_quality and task_tier in ["critical", "high"]:
            if status == BudgetStatus.EXCEEDED:
                # Even critical tasks can't run if budget exceeded
                logger.warning(f"Budget exceeded - cannot run {task_type} even with quality preservation")
                return None

            # Critical tasks: Always use at least the fallback (Sonnet minimum)
            # This ensures quality doesn't degrade significantly
            if status in [BudgetStatus.CRITICAL, BudgetStatus.WARNING]:
                logger.info(f"🛡️ Quality preserved for {task_type} - using {tier_config['fallback']}")
                return tier_config["fallback"]

            # Normal budget: use preferred model
            return tier_config["min_model"]

        # For standard/basic tasks, apply cost-saving measures
        if status == BudgetStatus.EXCEEDED:
            return None

        if status == BudgetStatus.CRITICAL:
            # Use only Haiku for non-critical tasks
            return "claude-3-haiku-20240307"

        if status == BudgetStatus.WARNING:
            # Use fallback for this tier
            return tier_config["fallback"]

        # Normal budget - use the preferred model for this tier
        return tier_config["min_model"]

    def get_quality_tier(self, task_type: str) -> str:
        """Get the quality tier for a task type."""
        for tier_name, tier_config in QUALITY_TIERS.items():
            if task_type in tier_config["tasks"]:
                return tier_name
        return "standard"

    def is_quality_critical(self, task_type: str) -> bool:
        """Check if a task type requires quality preservation."""
        return task_type in QUALITY_CRITICAL_TASKS

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def estimate_cost(self, model: str, input_text: str, estimated_output_tokens: int = 500) -> float:
        """Estimate cost before making a call."""
        input_tokens = self.estimate_tokens(input_text)
        return self.calculate_claude_cost(model, input_tokens, estimated_output_tokens)

    def get_daily_report(self) -> str:
        """Generate daily cost report."""
        status, info = self.get_budget_status()

        report = f"""
📊 Daily Cost Report - {datetime.now().strftime("%Y-%m-%d")}
{'=' * 50}

💰 Daily Spending:
   Spent: ${info['daily_spent_usd']:.4f} / ${info['daily_limit_usd']:.2f}
   Remaining: ${info['daily_remaining_usd']:.4f}
   Usage: {info['daily_percent']}%

📅 Monthly Spending:
   Spent: ${info['monthly_spent_usd']:.4f} / ${info['monthly_limit_usd']:.2f}
   Spent (INR): ₹{info['monthly_spent_inr']:.0f}
   Remaining: ${info['monthly_remaining_usd']:.4f}
   Usage: {info['monthly_percent']}%

🚦 Status: {status.value.upper()}

"""

        # Add recent calls summary
        recent_calls = self.data["calls"][-10:]
        if recent_calls:
            report += "📝 Recent Calls:\n"
            for call in recent_calls[-5:]:
                report += f"   • {call['model']}: ${call['cost_usd']:.4f} ({call['operation']})\n"

        return report


# ============================================================
# COST-AWARE API WRAPPER
# ============================================================

class CostAwareAPI:
    """
    Wrapper that adds cost tracking, caching, and quality-aware model selection.

    Key features:
    - Tracks all API costs
    - Caches responses to avoid duplicate calls
    - Quality-preserving model selection (critical tasks never downgraded)
    - Budget enforcement with graceful degradation
    """

    def __init__(self, preserve_quality: bool = True):
        self.tracker = CostTracker()
        self.cache = get_response_cache()
        self.preserve_quality = preserve_quality
        self._cost_savings = 0.0  # Track savings from caching

    def can_make_call(self, estimated_cost: float = 0.01) -> bool:
        """Check if we can make an API call."""
        return self.tracker.can_afford(estimated_cost)

    def get_model_for_task(self, task_type: str) -> Optional[str]:
        """Get appropriate model for task based on budget AND quality requirements."""
        return self.tracker.get_recommended_model(task_type, self.preserve_quality)

    def should_use_local_alternative(self, task_type: str = "general") -> bool:
        """
        Check if we should use local alternatives to save cost.

        QUALITY PRESERVATION: Never suggest local alternatives for critical tasks.
        """
        status, _ = self.tracker.get_budget_status()

        # Critical tasks should never use local alternatives
        if self.tracker.is_quality_critical(task_type):
            return False

        return status in [BudgetStatus.CRITICAL, BudgetStatus.EXCEEDED]

    def check_cache(self, prompt: str, model: str, task_type: str) -> Optional[str]:
        """Check if response is cached."""
        cached = self.cache.get(prompt, model, task_type)
        if cached:
            # Estimate the cost we saved
            estimated_cost = self.tracker.estimate_cost(model, prompt, 500)
            self._cost_savings += estimated_cost
        return cached

    def cache_response(self, prompt: str, model: str, task_type: str, response: str):
        """Cache a response."""
        self.cache.set(prompt, model, task_type, response)

    def record_call(self, api: str, model: str, input_tokens: int = 0,
                   output_tokens: int = 0, operation: str = "unknown") -> float:
        """Record an API call."""
        if api == "claude":
            return self.tracker.record_claude_call(model, input_tokens, output_tokens, operation)
        elif api == "kie":
            return self.tracker.record_kie_call(model, operation)
        return 0.0

    def get_cost_summary(self) -> dict:
        """Get cost summary including savings."""
        status, info = self.tracker.get_budget_status()
        cache_stats = self.cache.get_stats()

        return {
            **info,
            "cache_entries": cache_stats["entries"],
            "estimated_savings_usd": round(self._cost_savings, 4),
            "quality_preservation_enabled": self.preserve_quality
        }

    def get_smart_model(self, task_type: str, input_text: str,
                        max_cost: Optional[float] = None) -> Tuple[Optional[str], float]:
        """
        Get smart model recommendation with cost estimate.

        Returns:
            Tuple of (model_id, estimated_cost)
        """
        model = self.get_model_for_task(task_type)
        if not model:
            return None, 0.0

        estimated_cost = self.tracker.estimate_cost(model, input_text)

        # Check if we can afford it
        if max_cost and estimated_cost > max_cost:
            # Try a cheaper model if quality allows
            tier = self.tracker.get_quality_tier(task_type)
            if tier not in ["critical", "high"]:
                # Can downgrade
                model = "claude-3-haiku-20240307"
                estimated_cost = self.tracker.estimate_cost(model, input_text)

        return model, estimated_cost


# ============================================================
# COST OPTIMIZATION HELPERS
# ============================================================

def batch_similar_tasks(tasks: List[dict]) -> List[List[dict]]:
    """
    Batch similar tasks together to reduce API calls.

    This groups tasks by type and model so they can be processed
    more efficiently (e.g., single prompt with multiple items).
    """
    from collections import defaultdict
    batches = defaultdict(list)

    for task in tasks:
        task_type = task.get("type", "general")
        batches[task_type].append(task)

    return list(batches.values())


def estimate_batch_cost(tasks: List[dict], tracker: CostTracker) -> float:
    """Estimate total cost for a batch of tasks."""
    total = 0.0
    for task in tasks:
        task_type = task.get("type", "general")
        input_text = task.get("prompt", "")
        model = tracker.get_recommended_model(task_type)
        if model:
            total += tracker.estimate_cost(model, input_text)
    return total


# ============================================================
# GLOBAL INSTANCE
# ============================================================

# Global cost tracker instance
_cost_tracker = None

def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


def get_cost_aware_api() -> CostAwareAPI:
    """Get cost-aware API wrapper."""
    return CostAwareAPI()


# ============================================================
# CLI
# ============================================================

def print_status():
    """Print cost status."""
    tracker = get_cost_tracker()
    print(tracker.get_daily_report())


def print_detailed_report():
    """Print detailed cost breakdown."""
    tracker = get_cost_tracker()

    print("\n" + "=" * 60)
    print("  💰 Detailed Cost Report")
    print("=" * 60)

    # Monthly breakdown
    print("\n📅 Monthly Breakdown:")
    for month, cost in sorted(tracker.data.get("monthly_breakdown", {}).items()):
        inr = cost * BUDGET_CONFIG["exchange_rate_inr_usd"]
        print(f"   {month}: ${cost:.4f} (₹{inr:.0f})")

    # Daily breakdown (last 7 days)
    print("\n📆 Daily Breakdown (Last 7 days):")
    daily = tracker.data.get("daily_breakdown", {})
    sorted_days = sorted(daily.items(), reverse=True)[:7]
    for day, cost in sorted_days:
        print(f"   {day}: ${cost:.4f}")

    # API breakdown
    print("\n🔌 API Breakdown:")
    api_costs = {}
    for call in tracker.data.get("calls", []):
        api = call.get("api", "unknown")
        if api not in api_costs:
            api_costs[api] = 0.0
        api_costs[api] += call.get("cost_usd", 0)

    for api, cost in api_costs.items():
        print(f"   {api}: ${cost:.4f}")

    # Model breakdown
    print("\n🤖 Model Breakdown:")
    model_costs = {}
    for call in tracker.data.get("calls", []):
        model = call.get("model", "unknown")
        if model not in model_costs:
            model_costs[model] = {"cost": 0.0, "calls": 0}
        model_costs[model]["cost"] += call.get("cost_usd", 0)
        model_costs[model]["calls"] += 1

    for model, data in sorted(model_costs.items(), key=lambda x: x[1]["cost"], reverse=True):
        name = CLAUDE_PRICING.get(model, {}).get("name", model)
        print(f"   {name}: ${data['cost']:.4f} ({data['calls']} calls)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cost Tracker - Budget & Quality Management")
    parser.add_argument("--status", action="store_true", help="Show cost status")
    parser.add_argument("--detailed", action="store_true", help="Show detailed report")
    parser.add_argument("--reset-daily", action="store_true", help="Reset daily counter")
    parser.add_argument("--cache-stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--clear-cache", action="store_true", help="Clear response cache")
    parser.add_argument("--model", type=str, help="Get recommended model for task type")

    args = parser.parse_args()

    if args.detailed:
        print_detailed_report()
    elif args.reset_daily:
        tracker = get_cost_tracker()
        tracker.data["daily_spent_usd"] = 0.0
        tracker.save_data()
        print("✅ Daily counter reset!")
    elif args.cache_stats:
        cache = get_response_cache()
        stats = cache.get_stats()
        print(f"\n📦 Response Cache Statistics")
        print(f"{'=' * 40}")
        print(f"   Entries: {stats['entries']} / {stats['max_entries']}")
        print(f"   Enabled: {stats['enabled']}")
        print(f"\n💡 Cache helps avoid redundant API calls")
    elif args.clear_cache:
        cache = get_response_cache()
        cache.clear()
        print("✅ Cache cleared!")
    elif args.model:
        tracker = get_cost_tracker()
        model = tracker.get_recommended_model(args.model, preserve_quality=True)
        tier = tracker.get_quality_tier(args.model)
        print(f"\n🤖 Model Recommendation for '{args.model}'")
        print(f"{'=' * 40}")
        print(f"   Quality Tier: {tier}")
        print(f"   Recommended Model: {model}")
        if tracker.is_quality_critical(args.model):
            print(f"   ⚠️  Quality-critical: Won't be downgraded")
    else:
        print_status()
        print("\n💡 Tips:")
        print("   --detailed       Show full breakdown")
        print("   --cache-stats    View cache status")
        print("   --model <type>   Get model for task")
