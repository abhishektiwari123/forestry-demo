#!/usr/bin/env python3
"""
Pokemon AI Video Generator - Autonomous Improvement Daemon

This daemon runs 24/7 to continuously improve image/video generation quality
using Claude Vision API for analysis and feedback loops.

Features:
- Generates test images with current prompts
- Analyzes quality using Claude Vision API
- Identifies improvements and refines prompts
- Updates best practices based on learnings
- Logs all experiments and results

Run with: python scripts/auto_improvement_daemon.py
Or as service: systemctl start pokemon-ai-improver
"""

import os
import sys
import json
import time
import logging
import requests
import base64
import random
from datetime import datetime
from pathlib import Path
from io import BytesIO

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "auto_improvement.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
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

# API Keys
KIE_API_KEY = os.environ.get("KIE_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# File paths
BEST_PRACTICES_FILE = Path(__file__).parent / "best_practices.json"
LEARNINGS_FILE = Path(__file__).parent / "auto_learnings.json"
EXPERIMENTS_FILE = Path(__file__).parent / "experiments_log.json"

# Configuration
CONFIG = {
    "check_interval_seconds": 300,  # 5 minutes between improvement cycles
    "max_experiments_per_hour": 10,
    "min_quality_score": 7.0,  # Target quality score (1-10)
    "improvement_threshold": 0.5,  # Min improvement to save new prompt
    "pokemon_test_subjects": [
        ("Charizard", "Dragonite", "volcanic"),
        ("Pikachu", "Raichu", "thunderstorm"),
        ("Blastoise", "Gyarados", "ocean"),
        ("Gengar", "Alakazam", "haunted_mansion"),
        ("Mewtwo", "Lucario", "psychic_arena")
    ]
}


class AutoImprovementDaemon:
    """Autonomous improvement daemon for Pokemon AI Video Generator."""

    def __init__(self):
        self.running = True
        self.experiments_today = 0
        self.last_hour_reset = datetime.now().hour
        self.learnings = self.load_learnings()
        self.best_practices = self.load_best_practices()

    def load_learnings(self) -> dict:
        """Load previous learnings from file."""
        if LEARNINGS_FILE.exists():
            try:
                with open(LEARNINGS_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading learnings: {e}")
        return {
            "prompt_improvements": [],
            "quality_history": [],
            "best_prompts": {},
            "failed_patterns": [],
            "successful_patterns": []
        }

    def save_learnings(self):
        """Save learnings to file."""
        try:
            with open(LEARNINGS_FILE, 'w') as f:
                json.dump(self.learnings, f, indent=2, default=str)
            logger.info("Learnings saved successfully")
        except Exception as e:
            logger.error(f"Error saving learnings: {e}")

    def load_best_practices(self) -> dict:
        """Load best practices from file."""
        if BEST_PRACTICES_FILE.exists():
            try:
                with open(BEST_PRACTICES_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading best practices: {e}")
        return {"image_generation": {}, "video_generation": {}, "narration": {}}

    def save_best_practices(self):
        """Save updated best practices to file."""
        try:
            with open(BEST_PRACTICES_FILE, 'w') as f:
                json.dump(self.best_practices, f, indent=2, default=str)
            logger.info("Best practices updated and saved")
        except Exception as e:
            logger.error(f"Error saving best practices: {e}")

    def log_experiment(self, experiment: dict):
        """Log experiment results."""
        experiments = []
        if EXPERIMENTS_FILE.exists():
            try:
                with open(EXPERIMENTS_FILE) as f:
                    experiments = json.load(f)
            except:
                pass

        experiment["timestamp"] = datetime.now().isoformat()
        experiments.append(experiment)

        # Keep last 1000 experiments
        experiments = experiments[-1000:]

        with open(EXPERIMENTS_FILE, 'w') as f:
            json.dump(experiments, f, indent=2)

    def generate_test_image(self, prompt: str, negative_prompt: str = "") -> bytes | None:
        """Generate a test image using KIE API."""
        if not KIE_API_KEY:
            logger.error("KIE API key not found")
            return None

        headers = {
            "Authorization": f"Bearer {KIE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt or "blurry, low quality, distorted, deformed",
                "resolution": "2K",
                "aspect_ratio": "16:9",
                "num_images": 1
            }
        }

        try:
            # Create task
            response = requests.post(
                "https://api.kie.ai/api/v1/jobs/createTask",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"Image generation failed: {response.status_code}")
                return None

            result = response.json()
            task_id = result.get("data", {}).get("taskId")

            if not task_id:
                logger.error("No task ID returned")
                return None

            # Poll for completion
            for _ in range(60):  # Max 5 minutes
                time.sleep(5)

                status_response = requests.get(
                    f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
                    headers=headers,
                    timeout=30
                )

                if status_response.status_code == 200:
                    status_data = status_response.json().get("data", {})
                    status = status_data.get("status", "").lower()

                    if status in ["success", "completed"]:
                        result_json = status_data.get("resultJson")
                        if isinstance(result_json, str):
                            result_json = json.loads(result_json)

                        if isinstance(result_json, list) and len(result_json) > 0:
                            image_url = result_json[0].get("url")
                            if image_url:
                                # Download image
                                img_response = requests.get(image_url, timeout=60)
                                if img_response.status_code == 200:
                                    return img_response.content
                        break

                    elif status in ["failed", "error"]:
                        logger.error(f"Image generation failed: {status_data.get('error')}")
                        break

            return None

        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return None

    def analyze_image_with_claude(self, image_data: bytes, prompt_used: str, context: dict) -> dict:
        """Analyze generated image using Claude Vision API."""
        if not ANTHROPIC_API_KEY:
            logger.error("Anthropic API key not found")
            return {"error": "No API key"}

        image_base64 = base64.b64encode(image_data).decode('utf-8')

        system_prompt = """You are an expert image quality analyst specializing in AI-generated Pokemon art.
Analyze the image and provide detailed feedback.

Return a JSON object with these fields:
{
    "quality_score": <1-10 float>,
    "pokemon_accuracy": <1-10 float>,
    "composition_score": <1-10 float>,
    "style_consistency": <1-10 float>,
    "technical_issues": ["list of issues found"],
    "strengths": ["list of strong points"],
    "improvement_suggestions": ["specific actionable suggestions"],
    "prompt_improvements": ["suggested prompt modifications"],
    "overall_assessment": "brief summary"
}

Be critical but constructive. Focus on actionable improvements."""

        user_message = f"""Analyze this AI-generated Pokemon image.

Original prompt used: "{prompt_used}"

Pokemon: {context.get('pokemon1', 'Unknown')} vs {context.get('pokemon2', 'Unknown')}
Environment: {context.get('environment', 'Unknown')}

Provide your analysis as JSON:"""

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
                    "max_tokens": 2048,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": user_message
                            }
                        ]
                    }],
                    "system": system_prompt
                },
                timeout=90
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("content", [{}])[0].get("text", "")

                # Parse JSON from response
                # Handle markdown code blocks
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]

                try:
                    analysis = json.loads(text.strip())
                    return analysis
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Claude response as JSON")
                    return {"error": "JSON parse error", "raw_response": text[:500]}
            else:
                logger.error(f"Claude API error: {response.status_code}")
                return {"error": f"API error {response.status_code}"}

        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return {"error": str(e)}

    def improve_prompt_with_claude(self, original_prompt: str, analysis: dict, context: dict) -> str | None:
        """Use Claude to generate an improved prompt based on analysis."""
        if not ANTHROPIC_API_KEY:
            return None

        suggestions = analysis.get("prompt_improvements", [])
        issues = analysis.get("technical_issues", [])

        if not suggestions and not issues:
            logger.info("No improvements suggested")
            return None

        system_prompt = """You are an expert at crafting prompts for AI image generation.
Your task is to improve the given prompt based on the analysis feedback.

Rules:
1. Keep the core subject (Pokemon, action, environment)
2. Add specific details that address the issues
3. Use descriptive, visual language
4. Keep prompt under 300 words
5. Include style keywords that improve quality

Return ONLY the improved prompt text, nothing else."""

        user_message = f"""Original prompt: "{original_prompt}"

Issues found: {json.dumps(issues)}
Suggestions: {json.dumps(suggestions)}

Pokemon: {context.get('pokemon1')} vs {context.get('pokemon2')}
Environment: {context.get('environment')}

Generate the improved prompt:"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",  # Use Haiku for quick iteration
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": user_message}],
                    "system": system_prompt
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                improved_prompt = result.get("content", [{}])[0].get("text", "").strip()

                # Remove quotes if wrapped
                if improved_prompt.startswith('"') and improved_prompt.endswith('"'):
                    improved_prompt = improved_prompt[1:-1]

                return improved_prompt
            else:
                logger.error(f"Prompt improvement API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Prompt improvement error: {e}")
            return None

    def generate_base_prompt(self, pokemon1: str, pokemon2: str, environment: str) -> str:
        """Generate a base prompt for Pokemon battle image with consistent lighting."""
        # Environment-specific lighting settings for natural, consistent shadows
        lighting_settings = {
            "volcanic": "dramatic rim lighting from lava glow below, strong directional light from above-left casting consistent shadows to the right, volumetric light through volcanic smoke",
            "thunderstorm": "dynamic lightning illumination from above, consistent shadow direction downward-right, electric blue rim lighting on characters, dramatic contrast",
            "ocean": "soft diffused sunlight from above filtering through water, caustic light patterns, consistent underwater shadows pointing downward, ambient ocean glow",
            "haunted_mansion": "eerie moonlight from upper-left window, consistent long shadows to lower-right, subtle ghostly rim lighting, candlelight fill from below",
            "psychic_arena": "ethereal purple-pink ambient lighting from energy orbs, soft consistent shadows with slight glow edges, dramatic top-down key light"
        }
        
        lighting = lighting_settings.get(environment, "natural sunlight from upper-left, consistent shadows to lower-right, soft ambient fill")
        
        base_prompt = f"""Epic Pokemon battle scene: {pokemon1} facing {pokemon2} in a {environment.replace('_', ' ')} environment.

Lighting direction: {lighting}

Both Pokemon rendered with consistent shadow direction matching the key light source, 
natural shadow softness based on distance from ground, proper ambient occlusion where bodies meet surfaces.

High detail, dramatic composition, professional digital art style, volumetric lighting, 
cinematic quality, 8K resolution, sharp focus on both Pokemon."""
        
        return base_prompt

    def run_improvement_cycle(self):
        """Run one improvement cycle."""
        logger.info("=" * 60)
        logger.info("Starting improvement cycle")

        # Rate limiting
        current_hour = datetime.now().hour
        if current_hour != self.last_hour_reset:
            self.experiments_today = 0
            self.last_hour_reset = current_hour

        if self.experiments_today >= CONFIG["max_experiments_per_hour"]:
            logger.info(f"Rate limit reached ({CONFIG['max_experiments_per_hour']}/hour). Waiting...")
            return

        # Select random test subject
        pokemon1, pokemon2, environment = random.choice(CONFIG["pokemon_test_subjects"])

        context = {
            "pokemon1": pokemon1,
            "pokemon2": pokemon2,
            "environment": environment
        }

        # Generate base prompt with lighting consistency
        base_prompt = self.generate_base_prompt(pokemon1, pokemon2, environment)
        logger.info(f"Testing: {pokemon1} vs {pokemon2} in {environment}")
        logger.info(f"Base prompt: {base_prompt[:100]}...")

        # Generate image
        logger.info("Generating test image...")
        image_data = self.generate_test_image(base_prompt)

        if not image_data:
            logger.error("Failed to generate test image")
            self.log_experiment({
                "status": "failed",
                "stage": "image_generation",
                "context": context
            })
            return

        self.experiments_today += 1
        logger.info(f"Image generated ({len(image_data)} bytes)")

        # Analyze with Claude Vision
        logger.info("Analyzing image with Claude Vision...")
        analysis = self.analyze_image_with_claude(image_data, base_prompt, context)

        if "error" in analysis:
            logger.error(f"Analysis failed: {analysis.get('error')}")
            self.log_experiment({
                "status": "failed",
                "stage": "analysis",
                "context": context,
                "error": analysis.get("error")
            })
            return

        quality_score = analysis.get("quality_score", 0)
        logger.info(f"Quality score: {quality_score}/10")
        logger.info(f"Issues: {analysis.get('technical_issues', [])}")
        logger.info(f"Strengths: {analysis.get('strengths', [])}")

        # Store quality history
        self.learnings["quality_history"].append({
            "timestamp": datetime.now().isoformat(),
            "pokemon": f"{pokemon1}_vs_{pokemon2}",
            "environment": environment,
            "score": quality_score,
            "prompt": base_prompt[:200]
        })

        # Keep last 100 quality records
        self.learnings["quality_history"] = self.learnings["quality_history"][-100:]

        # Check if improvement needed
        if quality_score >= CONFIG["min_quality_score"]:
            logger.info(f"Quality score {quality_score} meets target. Saving as best prompt.")

            key = f"{pokemon1}_{pokemon2}_{environment}"
            if key not in self.learnings["best_prompts"] or \
               self.learnings["best_prompts"][key].get("score", 0) < quality_score:
                self.learnings["best_prompts"][key] = {
                    "prompt": base_prompt,
                    "score": quality_score,
                    "timestamp": datetime.now().isoformat()
                }

            # Record successful patterns
            for strength in analysis.get("strengths", []):
                if strength not in self.learnings["successful_patterns"]:
                    self.learnings["successful_patterns"].append(strength)
        else:
            # Try to improve
            logger.info("Quality below target. Generating improved prompt...")
            improved_prompt = self.improve_prompt_with_claude(base_prompt, analysis, context)

            if improved_prompt:
                logger.info(f"Improved prompt: {improved_prompt[:100]}...")

                # Test improved prompt
                logger.info("Testing improved prompt...")
                improved_image = self.generate_test_image(improved_prompt)

                if improved_image:
                    self.experiments_today += 1
                    improved_analysis = self.analyze_image_with_claude(
                        improved_image, improved_prompt, context
                    )

                    improved_score = improved_analysis.get("quality_score", 0)
                    logger.info(f"Improved quality score: {improved_score}/10")

                    improvement = improved_score - quality_score

                    if improvement >= CONFIG["improvement_threshold"]:
                        logger.info(f"Improvement successful! +{improvement:.2f} points")

                        # Save improved prompt
                        self.learnings["prompt_improvements"].append({
                            "timestamp": datetime.now().isoformat(),
                            "original_prompt": base_prompt,
                            "improved_prompt": improved_prompt,
                            "original_score": quality_score,
                            "improved_score": improved_score,
                            "improvement": improvement,
                            "context": context
                        })

                        # Update best prompt if applicable
                        key = f"{pokemon1}_{pokemon2}_{environment}"
                        if key not in self.learnings["best_prompts"] or \
                           self.learnings["best_prompts"][key].get("score", 0) < improved_score:
                            self.learnings["best_prompts"][key] = {
                                "prompt": improved_prompt,
                                "score": improved_score,
                                "timestamp": datetime.now().isoformat()
                            }

                        # Update best practices
                        self.update_best_practices(analysis, improved_analysis, context)
                    else:
                        logger.info(f"Improvement marginal ({improvement:.2f}). Discarding.")

                        # Record failed patterns
                        for issue in analysis.get("technical_issues", []):
                            if issue not in self.learnings["failed_patterns"]:
                                self.learnings["failed_patterns"].append(issue)

        # Save learnings
        self.save_learnings()

        # Log experiment
        self.log_experiment({
            "status": "completed",
            "context": context,
            "original_prompt": base_prompt,
            "quality_score": quality_score,
            "analysis_summary": analysis.get("overall_assessment", "")
        })

        logger.info("Improvement cycle completed")
        logger.info("=" * 60)

    def generate_base_prompt(self, pokemon1: str, pokemon2: str, environment: str) -> str:
        """Generate a base prompt for testing."""
        # Check if we have a best prompt for this combination
        key = f"{pokemon1}_{pokemon2}_{environment}"
        if key in self.learnings["best_prompts"]:
            return self.learnings["best_prompts"][key]["prompt"]

        # Generate new base prompt
        env_descriptions = {
            "volcanic": "volcanic battlefield with flowing lava, ash particles, orange glow",
            "thunderstorm": "dramatic thunderstorm with lightning strikes, dark clouds, rain",
            "ocean": "turbulent ocean waves, dramatic sky, water splashes",
            "haunted_mansion": "eerie haunted mansion, purple mist, ghostly atmosphere",
            "psychic_arena": "mystical arena with floating crystals, energy waves, cosmic backdrop"
        }

        env_desc = env_descriptions.get(environment, environment)

        # Use successful patterns if available
        style_keywords = "highly detailed, cinematic lighting, dynamic pose, dramatic composition"
        if self.learnings["successful_patterns"]:
            style_keywords = ", ".join(self.learnings["successful_patterns"][-5:])

        prompt = f"""Epic Pokemon battle scene: {pokemon1} facing {pokemon2} in a {env_desc}.
{pokemon1} in dynamic attack pose, energy gathering, powerful stance.
{pokemon2} bracing for impact, defensive position.
Environment: {env_desc}, particles in air, dramatic atmosphere.
Style: {style_keywords}, professional anime art, vibrant colors, sharp focus.
Camera: Wide cinematic shot, low angle, emphasizing scale and power."""

        return prompt

    def update_best_practices(self, original_analysis: dict, improved_analysis: dict, context: dict):
        """Update best practices based on successful improvements."""
        improvements = improved_analysis.get("strengths", [])

        if "image_generation" not in self.best_practices:
            self.best_practices["image_generation"] = {
                "effective_keywords": [],
                "avoid_keywords": [],
                "composition_tips": [],
                "style_recommendations": []
            }

        # Add new successful patterns
        for improvement in improvements:
            if improvement not in self.best_practices["image_generation"]["effective_keywords"]:
                self.best_practices["image_generation"]["effective_keywords"].append(improvement)

        # Add issues to avoid
        for issue in original_analysis.get("technical_issues", []):
            if issue not in self.best_practices["image_generation"]["avoid_keywords"]:
                self.best_practices["image_generation"]["avoid_keywords"].append(issue)

        # Keep lists manageable
        self.best_practices["image_generation"]["effective_keywords"] = \
            self.best_practices["image_generation"]["effective_keywords"][-50:]
        self.best_practices["image_generation"]["avoid_keywords"] = \
            self.best_practices["image_generation"]["avoid_keywords"][-30:]

        self.best_practices["last_updated"] = datetime.now().isoformat()
        self.save_best_practices()

    def run(self):
        """Main daemon loop."""
        logger.info("=" * 60)
        logger.info("Pokemon AI Auto-Improvement Daemon Starting")
        logger.info(f"KIE API Key: {'Found' if KIE_API_KEY else 'Missing'}")
        logger.info(f"Anthropic API Key: {'Found' if ANTHROPIC_API_KEY else 'Missing'}")
        logger.info(f"Check interval: {CONFIG['check_interval_seconds']} seconds")
        logger.info(f"Max experiments/hour: {CONFIG['max_experiments_per_hour']}")
        logger.info("=" * 60)

        if not KIE_API_KEY or not ANTHROPIC_API_KEY:
            logger.error("Missing API keys! Cannot start daemon.")
            return

        while self.running:
            try:
                self.run_improvement_cycle()
            except KeyboardInterrupt:
                logger.info("Shutdown requested...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in improvement cycle: {e}")
                import traceback
                traceback.print_exc()

            if self.running:
                logger.info(f"Sleeping for {CONFIG['check_interval_seconds']} seconds...")
                time.sleep(CONFIG["check_interval_seconds"])

        logger.info("Daemon stopped")
        self.save_learnings()


def print_status():
    """Print current daemon status and learnings."""
    print("\n" + "=" * 60)
    print("Pokemon AI Auto-Improvement Daemon - Status Report")
    print("=" * 60)

    if LEARNINGS_FILE.exists():
        with open(LEARNINGS_FILE) as f:
            learnings = json.load(f)

        print(f"\nTotal prompt improvements: {len(learnings.get('prompt_improvements', []))}")
        print(f"Quality history entries: {len(learnings.get('quality_history', []))}")
        print(f"Best prompts saved: {len(learnings.get('best_prompts', {}))}")
        print(f"Successful patterns: {len(learnings.get('successful_patterns', []))}")
        print(f"Failed patterns: {len(learnings.get('failed_patterns', []))}")

        # Recent quality scores
        history = learnings.get("quality_history", [])[-10:]
        if history:
            print("\nRecent quality scores:")
            for entry in history:
                print(f"  {entry.get('timestamp', 'N/A')[:16]} - {entry.get('pokemon', 'N/A')}: {entry.get('score', 0)}/10")

        # Best prompts
        best = learnings.get("best_prompts", {})
        if best:
            print("\nBest prompts by scenario:")
            for key, data in list(best.items())[:5]:
                print(f"  {key}: {data.get('score', 0)}/10")
    else:
        print("\nNo learnings file found. Daemon hasn't run yet.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pokemon AI Auto-Improvement Daemon")
    parser.add_argument("--status", action="store_true", help="Show current status and learnings")
    parser.add_argument("--once", action="store_true", help="Run single improvement cycle")
    args = parser.parse_args()

    if args.status:
        print_status()
    elif args.once:
        daemon = AutoImprovementDaemon()
        daemon.run_improvement_cycle()
    else:
        daemon = AutoImprovementDaemon()
        daemon.run()
