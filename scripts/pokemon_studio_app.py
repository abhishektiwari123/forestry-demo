#!/usr/bin/env python3
"""
Pokemon AI Video Generator Studio - Interactive Web UI

A step-by-step interactive workflow for generating Pokemon battle videos.
Each step requires manual approval before proceeding.

Run with: streamlit run scripts/pokemon_studio_app.py
"""

import streamlit as st
import requests
import json
import os
import time
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime

# Import our prompt validator
import sys
sys.path.insert(0, os.path.dirname(__file__))
from prompt_validator import PromptValidator, POKEMON_DETAILED_INFO

# Page config
st.set_page_config(
    page_title="Pokemon AI Video Studio",
    page_icon="🐉",
    layout="wide"
)

# Best practices file path
BEST_PRACTICES_FILE = os.path.join(os.path.dirname(__file__), "best_practices.json")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "negative_prompt" not in st.session_state:
    st.session_state.negative_prompt = ""
if "storyboard_path" not in st.session_state:
    st.session_state.storyboard_path = None
if "storyboard_image" not in st.session_state:
    st.session_state.storyboard_image = None
if "panels" not in st.session_state:
    st.session_state.panels = []
if "panel_images" not in st.session_state:
    st.session_state.panel_images = []
if "video_prompts" not in st.session_state:
    st.session_state.video_prompts = []
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []
if "validation_errors" not in st.session_state:
    st.session_state.validation_errors = []
if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = ""
if "prompt_updated_notice" not in st.session_state:
    st.session_state.prompt_updated_notice = None

# Load API key from secrets or environment
def get_api_key():
    # Try Streamlit secrets first
    try:
        return st.secrets["KIE_API_KEY"]
    except:
        pass

    # Try environment variable
    if os.environ.get("KIE_API_KEY"):
        return os.environ.get("KIE_API_KEY")

    # Try .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("KIE_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return ""


def get_anthropic_api_key():
    """Get Anthropic API key for Claude."""
    # Try Streamlit secrets first
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass

    # Try environment variable
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ.get("ANTHROPIC_API_KEY")

    # Try .env file in scripts directory
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    # Remove quotes if present
                    key = key.strip('"').strip("'")
                    return key

    # Try .env in current working directory
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    key = key.strip('"').strip("'")
                    return key

    # Try parent directory
    parent_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(parent_env):
        with open(parent_env) as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    key = key.strip('"').strip("'")
                    return key

    return ""


KIE_API_KEY = get_api_key()
ANTHROPIC_API_KEY = get_anthropic_api_key()

# Debug: Show if API keys are loaded at startup
print(f"[DEBUG] KIE_API_KEY loaded: {'Yes' if KIE_API_KEY else 'No'}")
print(f"[DEBUG] ANTHROPIC_API_KEY loaded: {'Yes' if ANTHROPIC_API_KEY else 'No'}")
if ANTHROPIC_API_KEY:
    print(f"[DEBUG] ANTHROPIC key: {ANTHROPIC_API_KEY[:10]}...{ANTHROPIC_API_KEY[-4:]}")


def load_best_practices() -> dict:
    """Load best practices from JSON file."""
    if os.path.exists(BEST_PRACTICES_FILE):
        try:
            with open(BEST_PRACTICES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"practices": [], "prompt_improvements": []}


def save_best_practices(data: dict):
    """Save best practices to JSON file."""
    try:
        with open(BEST_PRACTICES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.warning(f"Could not save best practices: {e}")


def call_claude_for_prompt_improvement(current_prompt: str, feedback: str, failed_checks: list) -> tuple[str, str]:
    """
    Call Claude API to intelligently improve the prompt based on feedback.
    Returns (improved_prompt, best_practice_learned)
    """
    if not ANTHROPIC_API_KEY:
        # Fallback to simple append if no API key
        st.warning("⚠️ No Anthropic API key found. Using simple feedback append.")
        return None, None

    # Debug: Show API key is loaded (first/last 4 chars only)
    st.info(f"🔑 API Key loaded: {ANTHROPIC_API_KEY[:7]}...{ANTHROPIC_API_KEY[-4:]}")

    # Build the request to Claude
    failed_checks_text = ", ".join(failed_checks) if failed_checks else "None"

    system_prompt = """You are an expert at crafting image generation prompts for Nano Banana Pro AI model.
Your task is to improve a Pokemon battle storyboard prompt based on user feedback.

Rules:
1. Keep the same structure (4-panel split-screen format)
2. Make specific, targeted improvements based on the feedback
3. Don't remove existing good elements
4. Be more explicit about what failed
5. Extract a "best practice" lesson that can be applied to future prompts

IMPORTANT: Respond with ONLY raw JSON (no markdown code blocks). Format:
{"improved_prompt": "the full improved prompt text", "best_practice": "A concise lesson learned", "changes_made": "Brief summary of what you changed"}"""

    user_message = f"""Current prompt:
{current_prompt}

User feedback: {feedback}

Failed validation checks: {failed_checks_text}

Please improve this prompt to address the feedback and failed checks. Return ONLY raw JSON."""

    try:
        st.info("📡 Calling Claude API...")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",  # Use stable model ID
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": user_message}],
                "system": system_prompt
            },
            timeout=90  # Increase timeout
        )

        st.info(f"📡 API Response: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")

            # Clean up potential markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            elif content.startswith("```"):
                content = content[3:]  # Remove ```
            if content.endswith("```"):
                content = content[:-3]  # Remove trailing ```
            content = content.strip()

            # Parse JSON response
            try:
                parsed = json.loads(content)
                improved_prompt = parsed.get("improved_prompt")
                best_practice = parsed.get("best_practice")
                changes_made = parsed.get("changes_made", "")

                if improved_prompt:
                    st.success(f"✅ Claude improved the prompt! Changes: {changes_made}")
                    return improved_prompt, best_practice
                else:
                    st.warning("⚠️ Claude response missing improved_prompt")
                    return None, None
            except json.JSONDecodeError as e:
                st.warning(f"⚠️ Could not parse Claude response as JSON: {e}")
                st.code(content[:500])  # Show first 500 chars for debugging
                return None, None
        else:
            st.error(f"❌ Claude API error: {response.status_code} - {response.text[:200]}")
            return None, None

    except Exception as e:
        st.warning(f"Claude API error: {e}")
        return None, None

# Create validator
validator = PromptValidator()

# Demo mode - create sample images when API is unavailable
DEMO_MODE = False  # Will be set to True if API fails


def create_demo_storyboard():
    """Create a demo storyboard image with colored panels."""
    from PIL import ImageDraw, ImageFont

    # Create a 1600x900 image (16:9)
    img = Image.new('RGB', (1600, 900), color='#2a2a2a')
    draw = ImageDraw.Draw(img)

    # Panel colors and labels
    panels = [
        ((0, 0, 800, 450), '#ff6b6b', 'Panel 1: Charizard attacks'),
        ((800, 0, 1600, 450), '#ffa500', 'Panel 2: Dragonite hit'),
        ((0, 450, 800, 900), '#4ecdc4', 'Panel 3: Dragonite charges'),
        ((800, 450, 1600, 900), '#9b59b6', 'Panel 4: Counter attack'),
    ]

    for (x1, y1, x2, y2), color, label in panels:
        # Draw panel background
        draw.rectangle([x1+5, y1+5, x2-5, y2-5], fill=color)
        # Draw label
        text_x = x1 + (x2 - x1) // 2 - 100
        text_y = y1 + (y2 - y1) // 2 - 10
        draw.text((text_x, text_y), label, fill='white')

    # Add demo watermark
    draw.text((700, 430), "DEMO MODE - Sample Image", fill='yellow')

    return img


def log_feedback(step: str, feedback: str, action: str):
    """Log user feedback for each step."""
    st.session_state.feedback_log.append({
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "feedback": feedback,
        "action": action
    })


def call_kie_api(endpoint: str, payload: dict = None, method: str = "GET"):
    """Call KIE API using requests library."""
    # Updated API endpoint (changed from api.kieai.erweima.ai to api.kie.ai)
    base_url = "https://api.kie.ai/api/v1"
    headers = {
        "Authorization": f"Bearer {KIE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        if method == "POST":
            response = requests.post(
                f"{base_url}/{endpoint}",
                headers=headers,
                json=payload,
                timeout=60,
                verify=False  # Skip SSL verification
            )
        else:
            response = requests.get(
                f"{base_url}/{endpoint}",
                headers=headers,
                timeout=60,
                verify=False
            )

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}


def download_image(url: str) -> Image.Image:
    """Download image from URL and return as PIL Image."""
    try:
        response = requests.get(url, timeout=120, verify=False)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"Download error: {e}")
    return None


def incorporate_feedback_into_prompt(prompt: str, feedback: str) -> str:
    """Use feedback to improve the prompt."""
    if not feedback.strip():
        return prompt

    # Add feedback as additional instructions
    feedback_section = f"""

=== USER FEEDBACK TO INCORPORATE ===
{feedback}

=== ADJUSTED REQUIREMENTS ===
Please ensure the above feedback is addressed in the generated image.
"""
    return prompt + feedback_section


# ============================================================================
# HEADER
# ============================================================================
st.title("🐉 Pokemon AI Video Studio")
st.markdown("**Interactive step-by-step workflow for Pokemon battle video generation**")

# API Key check
if not KIE_API_KEY:
    st.error("⚠️ KIE_API_KEY not found! Add it to Streamlit secrets or .env file")
    st.code("""
# In Streamlit Cloud, go to Settings > Secrets and add:
KIE_API_KEY = "your-api-key-here"
    """)
    st.stop()

# Progress indicator
steps = ["1. Setup", "2. Prompt", "3. Generate", "4. Split", "5. Upscale", "6. Video"]
cols = st.columns(6)
for i, (col, step_name) in enumerate(zip(cols, steps)):
    if i + 1 < st.session_state.step:
        col.markdown(f"✅ {step_name}")
    elif i + 1 == st.session_state.step:
        col.markdown(f"🔵 **{step_name}**")
    else:
        col.markdown(f"⚪ {step_name}")

st.divider()

# ============================================================================
# STEP 1: SETUP
# ============================================================================
if st.session_state.step == 1:
    st.header("Step 1: Setup Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Select Pokemon")
        pokemon1 = st.selectbox(
            "Pokemon 1 (Attacker first)",
            list(POKEMON_DETAILED_INFO.keys()),
            format_func=lambda x: x.title()
        )
        pokemon2 = st.selectbox(
            "Pokemon 2 (Counter attacker)",
            [p for p in POKEMON_DETAILED_INFO.keys() if p != pokemon1],
            format_func=lambda x: x.title()
        )

        st.session_state.pokemon = [pokemon1.title(), pokemon2.title()]

    with col2:
        st.subheader("Environment")
        environment = st.selectbox(
            "Battle Environment",
            ["volcanic", "forest", "ocean", "cave", "urban", "mountain"]
        )
        st.session_state.environment = environment

    # Show Pokemon info
    st.subheader("Selected Pokemon Details")
    info_col1, info_col2 = st.columns(2)

    with info_col1:
        info1 = POKEMON_DETAILED_INFO.get(pokemon1, {})
        st.markdown(f"**{pokemon1.title()}**")
        st.write(f"Type: {info1.get('type', 'Unknown')}")
        st.write(f"Color: {info1.get('body_color', 'Unknown')}")
        attacks1 = list(info1.get('attacks', {}).keys())
        st.write(f"Attacks: {', '.join(attacks1[:3])}")

    with info_col2:
        info2 = POKEMON_DETAILED_INFO.get(pokemon2, {})
        st.markdown(f"**{pokemon2.title()}**")
        st.write(f"Type: {info2.get('type', 'Unknown')}")
        st.write(f"Color: {info2.get('body_color', 'Unknown')}")
        attacks2 = list(info2.get('attacks', {}).keys())
        st.write(f"Attacks: {', '.join(attacks2[:3])}")

    st.divider()

    if st.button("✅ Proceed to Prompt Generation", type="primary"):
        st.session_state.step = 2
        st.rerun()


# ============================================================================
# STEP 2: PROMPT GENERATION & REVIEW
# ============================================================================
elif st.session_state.step == 2:
    st.header("Step 2: Prompt Generation & Review")

    # Initialize prompt improvement history if not exists
    if "prompt_improvements" not in st.session_state:
        st.session_state.prompt_improvements = []

    # Load saved best practices
    best_practices_data = load_best_practices()

    # Generate prompt if not already done
    if not st.session_state.prompt:
        # Use OPTIMIZED format (proven to produce better quality)
        # Returns dict with prompt, negative_prompt, and generation parameters
        prompt_config = validator.generate_optimized_storyboard_prompt(
            pokemon_names=st.session_state.pokemon,
            environment=st.session_state.environment
        )
        st.session_state.prompt = prompt_config["prompt"]
        st.session_state.negative_prompt = prompt_config["negative_prompt"]
        # KIE API uses resolution and aspect_ratio, NOT width/height
        st.session_state.gen_params = {
            "model": prompt_config.get("model", "nano-banana-pro"),
            "resolution": prompt_config.get("resolution", "2K"),
            "aspect_ratio": prompt_config.get("aspect_ratio", "16:9"),
            "output_format": prompt_config.get("output_format", "png")
        }

    # Show saved best practices
    if best_practices_data.get("practices"):
        with st.expander("📚 Saved Best Practices (from previous sessions)", expanded=False):
            st.success("**Lessons learned from previous generations:**")
            for i, practice in enumerate(best_practices_data["practices"][-10:], 1):  # Show last 10
                st.markdown(f"**{i}.** {practice.get('lesson', practice)}")
                if isinstance(practice, dict) and practice.get('date'):
                    st.caption(f"Added: {practice['date']}")

    # Show accumulated prompt improvements from current session
    if st.session_state.prompt_improvements:
        with st.expander("📝 Current Session Feedback History", expanded=True):
            st.warning("**Feedback incorporated into prompt this session:**")
            for i, improvement in enumerate(st.session_state.prompt_improvements, 1):
                st.markdown(f"**{i}. {improvement['type']}:**")
                st.caption(improvement['feedback'])
                if improvement.get('failed_checks'):
                    st.caption(f"Failed checks: {', '.join(improvement['failed_checks'])}")
                if improvement.get('best_practice'):
                    st.success(f"💡 Lesson: {improvement['best_practice']}")

    st.subheader("Generated Prompt")
    st.info("Review the prompt below. You can edit it before generating the image.")

    # Editable prompt
    edited_prompt = st.text_area(
        "Storyboard Prompt (editable)",
        value=st.session_state.prompt,
        height=400
    )

    with st.expander("View Negative Prompt"):
        edited_negative = st.text_area(
            "Negative Prompt",
            value=st.session_state.negative_prompt,
            height=100
        )
        st.session_state.negative_prompt = edited_negative

    # Show generation parameters
    with st.expander("View Generation Parameters"):
        gen_params = st.session_state.get("gen_params", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model", gen_params.get('model', 'nano-banana-pro'))
        with col2:
            st.metric("Resolution", gen_params.get('resolution', '2K'))
        with col3:
            st.metric("Aspect Ratio", gen_params.get('aspect_ratio', '1:1'))
        st.info("Using Nano Banana Pro with 2K resolution for better 4-panel quality")

    # Validation
    st.subheader("🔍 Prompt Validation")
    validation = validator.validate_storyboard_prompt(
        edited_prompt,
        panel_count=4,
        pokemon_names=st.session_state.pokemon
    )

    # Show validation results in colored boxes
    col1, col2 = st.columns(2)
    with col1:
        if validation.passed:
            st.success(f"✅ Validation PASSED (Score: {validation.score:.2f})")
        else:
            st.error(f"❌ Validation FAILED (Score: {validation.score:.2f})")

    with col2:
        st.metric("Validation Score", f"{validation.score:.0%}")

    # Show issues, warnings, suggestions in expandable sections
    if validation.issues:
        st.error("**Issues (Must Fix):**")
        for issue in validation.issues:
            st.markdown(f"- ❌ {issue}")
        st.session_state.validation_errors = validation.issues

    if validation.warnings:
        st.warning("**Warnings:**")
        for warning in validation.warnings:
            st.markdown(f"- ⚠️ {warning}")

    if validation.suggestions:
        st.info("**Suggestions:**")
        for suggestion in validation.suggestions:
            st.markdown(f"- 💡 {suggestion}")

    # Manual Checklist
    st.subheader("📋 Manual Checklist")
    check1 = st.checkbox(f"{st.session_state.pokemon[0]} positioned on LEFT, facing RIGHT", key="check1")
    check2 = st.checkbox(f"{st.session_state.pokemon[1]} positioned on RIGHT, facing LEFT", key="check2")
    check3 = st.checkbox("Attack effects explicitly described (VISIBLE beams)", key="check3")
    check4 = st.checkbox("Battle damage continuity mentioned for panels 3-4", key="check4")
    check5 = st.checkbox("Photorealistic style enforced (no anime/cartoon)", key="check5")

    all_checked = all([check1, check2, check3, check4, check5])

    # Feedback Section
    st.subheader("📝 Your Feedback")
    feedback = st.text_area(
        "Add notes/feedback to improve the prompt:",
        value=st.session_state.user_feedback,
        key="prompt_feedback",
        placeholder="e.g., 'Make the fire attack more prominent', 'Dragonite should look more aggressive'"
    )
    st.session_state.user_feedback = feedback

    # Collect failed checks for feedback
    failed_checklist = []
    if not check1:
        failed_checklist.append(f"{st.session_state.pokemon[0]} not positioned on LEFT facing RIGHT")
    if not check2:
        failed_checklist.append(f"{st.session_state.pokemon[1]} not positioned on RIGHT facing LEFT")
    if not check3:
        failed_checklist.append("Attack effects not explicitly described with VISIBLE beams")
    if not check4:
        failed_checklist.append("Battle damage continuity not mentioned for panels 3-4")
    if not check5:
        failed_checklist.append("Photorealistic style not enforced")

    # Incorporate Feedback Button - uses Claude API
    if feedback.strip() or failed_checklist:
        if st.button("🤖 Improve Prompt with Claude AI", type="secondary"):
            # Combine feedback and failed checks
            all_feedback_parts = []
            if failed_checklist:
                all_feedback_parts.append("CHECKLIST ISSUES: " + "; ".join(failed_checklist))
            if feedback.strip():
                all_feedback_parts.append("USER FEEDBACK: " + feedback.strip())

            combined_feedback = " | ".join(all_feedback_parts)

            # Simple synchronous call with spinner
            with st.spinner("🤖 Claude AI is improving your prompt... (this may take 10-30 seconds)"):
                import time as time_module
                start_time = time_module.time()

                improved_prompt, best_practice = call_claude_for_prompt_improvement(
                    edited_prompt,
                    combined_feedback,
                    failed_checklist
                )

                elapsed = int(time_module.time() - start_time)

            if improved_prompt:
                st.session_state.prompt = improved_prompt

                # Save best practice
                if best_practice:
                    bp_data = load_best_practices()
                    bp_data["practices"].append({
                        "lesson": best_practice,
                        "date": datetime.now().isoformat(),
                        "feedback": combined_feedback,
                        "stage": "prompt_review"
                    })
                    save_best_practices(bp_data)

                # Store in session history
                if "prompt_improvements" not in st.session_state:
                    st.session_state.prompt_improvements = []
                st.session_state.prompt_improvements.append({
                    "type": "Prompt Review Improvement",
                    "feedback": combined_feedback,
                    "failed_checks": failed_checklist,
                    "best_practice": best_practice,
                    "used_claude": True
                })

                st.success(f"✅ Prompt improved by Claude AI! (took {elapsed}s)")
                st.session_state.user_feedback = ""
                time_module.sleep(1)
                st.rerun()
            else:
                # Fallback to simple append
                st.session_state.prompt = incorporate_feedback_into_prompt(edited_prompt, combined_feedback)
                st.warning("⚠️ Claude API issue. Feedback appended to prompt instead.")
                st.session_state.user_feedback = ""
                time_module.sleep(1)
                st.rerun()

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Setup"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🔄 Regenerate Prompt"):
            st.session_state.prompt = ""
            st.session_state.user_feedback = ""
            st.rerun()
    with col3:
        if not all_checked:
            st.warning("Complete all checklist items to proceed")
        if st.button("✅ Approve & Generate Image", type="primary", disabled=not all_checked):
            st.session_state.prompt = edited_prompt
            log_feedback("prompt", feedback, "approved")
            st.session_state.step = 3
            st.rerun()


# ============================================================================
# STEP 3: IMAGE GENERATION
# ============================================================================
elif st.session_state.step == 3:
    st.header("Step 3: Storyboard Image Generation")

    # Show notification if prompt was updated
    if st.session_state.prompt_updated_notice:
        st.success(f"🔄 {st.session_state.prompt_updated_notice}")
        st.session_state.prompt_updated_notice = None  # Clear after showing

    if st.session_state.storyboard_image is not None:
        # Already generated - show result
        st.success("✅ Storyboard generated!")
        st.image(st.session_state.storyboard_image, caption="Generated Storyboard", use_container_width=True)

        # Analysis
        img = st.session_state.storyboard_image
        st.write(f"Image size: {img.size[0]}x{img.size[1]}")
        st.write(f"Aspect ratio: {img.size[0]/img.size[1]:.2f}")

        # Manual review with validation
        st.subheader("🔍 Image Validation Checklist")

        img_checks = {
            "panel1_pokemon1": st.checkbox(f"Panel 1: {st.session_state.pokemon[0]} visible on LEFT?", key="img_c1"),
            "panel1_pokemon2": st.checkbox(f"Panel 1: {st.session_state.pokemon[1]} visible on RIGHT?", key="img_c2"),
            "panel1_attack": st.checkbox("Panel 1: Attack beam/effect visible?", key="img_c3"),
            "facing": st.checkbox("All panels: Both Pokemon FACING each other?", key="img_c4"),
            "damage": st.checkbox("Panels 3-4: Battle damage visible on Dragonite?", key="img_c5"),
            "style": st.checkbox("Style: Photorealistic (NOT anime/cartoon)?", key="img_c6"),
            "no_borders": st.checkbox("No thick borders between panels?", key="img_c7"),
        }

        failed_checks = [k for k, v in img_checks.items() if not v]
        passed_checks = [k for k, v in img_checks.items() if v]

        if failed_checks:
            st.error(f"❌ {len(failed_checks)} validation checks failed")
            st.session_state.validation_errors = failed_checks
        else:
            st.success("✅ All validation checks passed!")

        # Feedback for regeneration
        st.subheader("📝 Feedback for Regeneration")

        # Show failed checks as auto-generated feedback
        if failed_checks:
            failed_check_labels = {
                "panel1_pokemon1": f"{st.session_state.pokemon[0]} not visible on LEFT in Panel 1",
                "panel1_pokemon2": f"{st.session_state.pokemon[1]} not visible on RIGHT in Panel 1",
                "panel1_attack": "Attack beam/effect not visible in Panel 1",
                "facing": "Pokemon not facing each other in all panels",
                "damage": f"Battle damage not visible on {st.session_state.pokemon[1]} in Panels 3-4",
                "style": "Style looks like anime/cartoon instead of photorealistic",
                "no_borders": "Thick borders visible between panels",
            }
            auto_feedback = [failed_check_labels.get(fc, fc) for fc in failed_checks]
            st.warning("**Issues detected from checklist:**")
            for issue in auto_feedback:
                st.markdown(f"- {issue}")

        feedback = st.text_area(
            "Additional feedback (what needs to be fixed?):",
            key="image_feedback",
            placeholder="e.g., 'Dragonite is facing away', 'Fire attack looks weak', 'Colors are too dark'"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Prompt"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("🔄 Regenerate with Feedback"):
                # Combine failed checks and manual feedback
                all_feedback_parts = []

                # Add failed checks as feedback
                if failed_checks:
                    failed_check_labels = {
                        "panel1_pokemon1": f"{st.session_state.pokemon[0]} must be visible on LEFT in Panel 1",
                        "panel1_pokemon2": f"{st.session_state.pokemon[1]} must be visible on RIGHT in Panel 1",
                        "panel1_attack": "Attack beam/effect must be clearly visible in Panel 1",
                        "facing": "Both Pokemon must be FACING each other in ALL panels",
                        "damage": f"Battle damage must be visible on {st.session_state.pokemon[1]} in Panels 3-4",
                        "style": "Style must be PHOTOREALISTIC, NOT anime or cartoon",
                        "no_borders": "No thick borders between panels",
                    }
                    check_feedback = [failed_check_labels.get(fc, fc) for fc in failed_checks]
                    all_feedback_parts.append("FAILED CHECKS: " + "; ".join(check_feedback))

                # Add manual feedback
                if feedback.strip():
                    all_feedback_parts.append("USER FEEDBACK: " + feedback.strip())

                combined_feedback = " | ".join(all_feedback_parts)

                if combined_feedback:
                    # Try to use Claude API for intelligent prompt improvement
                    with st.spinner("🤖 Using Claude AI to improve prompt..."):
                        improved_prompt, best_practice = call_claude_for_prompt_improvement(
                            st.session_state.prompt,
                            combined_feedback,
                            failed_checks
                        )

                    if improved_prompt:
                        # Claude successfully improved the prompt
                        st.session_state.prompt = improved_prompt
                        st.session_state.prompt_updated_notice = "Prompt improved by Claude AI! Review the updated prompt below."

                        # Save best practice to file
                        if best_practice:
                            bp_data = load_best_practices()
                            bp_data["practices"].append({
                                "lesson": best_practice,
                                "date": datetime.now().isoformat(),
                                "feedback": combined_feedback
                            })
                            save_best_practices(bp_data)
                    else:
                        # Fallback to simple append
                        st.session_state.prompt = incorporate_feedback_into_prompt(
                            st.session_state.prompt,
                            f"PREVIOUS IMAGE ISSUES: {combined_feedback}"
                        )
                        st.session_state.prompt_updated_notice = "Feedback appended to prompt (Claude API unavailable)."

                    # Store in session improvement history
                    if "prompt_improvements" not in st.session_state:
                        st.session_state.prompt_improvements = []
                    st.session_state.prompt_improvements.append({
                        "type": "Image Regeneration",
                        "feedback": combined_feedback,
                        "failed_checks": failed_checks,
                        "best_practice": best_practice if best_practice else None,
                        "used_claude": improved_prompt is not None
                    })

                st.session_state.storyboard_image = None
                log_feedback("image", combined_feedback, "regenerate")
                st.rerun()
        with col3:
            can_proceed = len(failed_checks) == 0
            if st.button("✅ Approve & Split Panels", type="primary", disabled=not can_proceed):
                log_feedback("image", feedback, "approved")
                st.session_state.step = 4
                st.rerun()
            if not can_proceed:
                st.caption("Complete all checks to proceed")

    else:
        # Need to generate
        st.info("Click below to generate the storyboard image from your approved prompt.")

        with st.expander("View Prompt", expanded=False):
            st.text(st.session_state.prompt)

        col1, col2 = st.columns(2)

        with col1:
            generate_clicked = st.button("🎨 Generate Storyboard", type="primary")

        with col2:
            demo_clicked = st.button("🎭 Use Demo Mode", type="secondary",
                                     help="Use sample image to test workflow without API")

        if demo_clicked:
            st.session_state.storyboard_image = create_demo_storyboard()
            st.session_state.demo_mode = True
            st.success("✅ Demo storyboard created!")
            st.rerun()

        if generate_clicked:
            with st.spinner("Generating storyboard... This may take 30-60 seconds"):
                # Submit generation request using Nano Banana Pro API format
                # API: POST /api/v1/jobs/createTask
                # Model: nano-banana-pro (NOT google/nano-banana)
                # Uses: resolution (1K, 2K, 4K) and aspect_ratio

                # Get generation parameters (or use defaults)
                gen_params = st.session_state.get("gen_params", {
                    "model": "nano-banana-pro",
                    "resolution": "2K",
                    "aspect_ratio": "1:1",
                    "output_format": "png"
                })

                payload = {
                    "model": gen_params.get("model", "nano-banana-pro"),
                    "input": {
                        "prompt": st.session_state.prompt,
                        "image_input": [],
                        "aspect_ratio": gen_params.get("aspect_ratio", "1:1"),
                        "resolution": gen_params.get("resolution", "2K"),
                        "output_format": gen_params.get("output_format", "png")
                    }
                }

                response = call_kie_api("jobs/createTask", payload, method="POST")

                # Check for None or error response
                if response is None:
                    st.error("API Error: No response from server")
                    st.warning("💡 The API is not accessible. Click **Use Demo Mode** to test the workflow with sample images.")
                elif "error" in response:
                    st.error(f"API Error: {response['error']}")
                    st.warning("💡 The API is not accessible. Click **Use Demo Mode** to test the workflow with sample images.")
                elif response.get("code") != 200:
                    # New API uses 'msg' instead of 'message'
                    error_msg = response.get('msg') or response.get('message') or 'Unknown error'
                    st.error(f"API Error: {error_msg} (Code: {response.get('code')})")
                    st.warning("💡 Check your API key or try Demo Mode.")
                else:
                    task_id = response.get("data", {}).get("taskId")

                    if not task_id:
                        st.error(f"Failed to submit generation task. Response: {response}")
                    else:
                        st.write(f"Task ID: {task_id}")
                        progress = st.progress(0)
                        status_text = st.empty()

                        # Poll for completion
                        for i in range(60):
                            time.sleep(5)
                            progress.progress((i + 1) / 60)
                            status_text.text(f"Waiting for generation... ({(i+1)*5}s)")

                            status = call_kie_api(f"jobs/recordInfo?taskId={task_id}")

                            if status is None or "error" in status:
                                continue

                            state = (status.get("data") or {}).get("state", "").lower()

                            if state == "success":
                                result_json = status.get("data", {}).get("resultJson", "{}")
                                if isinstance(result_json, str):
                                    result_json = json.loads(result_json)

                                urls = result_json.get("resultUrls", [])
                                if urls:
                                    img = download_image(urls[0])
                                    if img:
                                        st.session_state.storyboard_image = img
                                        st.success("✅ Generated successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to download image")
                                break

                            elif state in ["failed", "error"]:
                                st.error(f"Generation failed: {status.get('data', {}).get('failMsg')}")
                                break

                        else:
                            st.error("Timeout - generation took too long")


# ============================================================================
# STEP 4: PANEL SPLITTING
# ============================================================================
elif st.session_state.step == 4:
    st.header("Step 4: Panel Splitting & Validation")

    if st.session_state.panel_images:
        # Already split - show panels
        st.success("✅ Panels extracted!")

        # Initialize selected panels if not exists
        if "selected_panels" not in st.session_state:
            st.session_state.selected_panels = [True] * len(st.session_state.panel_images)

        cols = st.columns(2)
        for i, panel_img in enumerate(st.session_state.panel_images):
            with cols[i % 2]:
                st.image(panel_img, caption=f"Panel {i+1}", use_container_width=True)
                st.caption(f"Size: {panel_img.size[0]}x{panel_img.size[1]}")
                # Add skip checkbox
                st.session_state.selected_panels[i] = st.checkbox(
                    f"✅ Include Panel {i+1} for video generation",
                    value=st.session_state.selected_panels[i],
                    key=f"select_panel_{i}"
                )

        # Show selected count
        selected_count = sum(st.session_state.selected_panels)
        st.info(f"📊 {selected_count} of {len(st.session_state.panel_images)} panels selected for video generation")

        # Panel-by-panel validation
        st.subheader("🔍 Panel Validation")

        panel_checks = {}
        panel_issues = []
        for i in range(len(st.session_state.panel_images)):
            if not st.session_state.selected_panels[i]:
                continue  # Skip validation for unselected panels
            with st.expander(f"Panel {i+1} Review", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    ok = st.checkbox(f"Panel {i+1} content correct", key=f"panel_{i}_ok")
                    panel_checks[f"panel_{i+1}_content"] = ok
                with col2:
                    border_ok = st.checkbox(f"No visible borders/edges", key=f"panel_{i}_border")
                    panel_checks[f"panel_{i+1}_borders"] = border_ok

                notes = st.text_input(f"Issues with Panel {i+1}", key=f"panel_{i}_notes")
                if notes:
                    panel_issues.append(f"Panel {i+1}: {notes}")

        # Border check
        st.subheader("Border Check")
        has_borders = st.radio(
            "Are there visible frame borders in any panel?",
            ["No borders visible ✅", "Some borders visible ⚠️", "Heavy borders visible ❌"],
            key="border_check"
        )

        # Collect failed checks
        failed_panel_checks = [k for k, v in panel_checks.items() if not v]
        if "Heavy borders" in has_borders:
            failed_panel_checks.append("heavy_borders_between_panels")
        elif "Some borders" in has_borders:
            failed_panel_checks.append("some_borders_visible")

        # Show failed checks as auto-feedback
        if failed_panel_checks or panel_issues:
            st.warning("**Issues detected:**")
            for check in failed_panel_checks:
                if "content" in check:
                    panel_num = check.split("_")[1]
                    st.markdown(f"- Panel {panel_num} content not correct")
                elif "borders" in check and "panel" in check:
                    panel_num = check.split("_")[1]
                    st.markdown(f"- Panel {panel_num} has visible borders")
                elif "heavy_borders" in check:
                    st.markdown("- Heavy borders visible between panels")
                elif "some_borders" in check:
                    st.markdown("- Some borders visible between panels")
            for issue in panel_issues:
                st.markdown(f"- {issue}")

        feedback = st.text_area("Additional feedback on panels:", key="split_feedback",
                               placeholder="e.g., 'Panel 2 is cut off', 'Pokemon not fully visible in panel 3'")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⬅️ Back to Image"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("🔄 Re-split with Different Margins"):
                st.session_state.panel_images = []
                st.rerun()
        with col3:
            # Button to go back and regenerate with feedback
            if st.button("🔄 Regenerate Image"):
                # Combine panel issues and feedback
                all_feedback_parts = []

                if failed_panel_checks:
                    check_labels = []
                    for check in failed_panel_checks:
                        if "content" in check:
                            panel_num = check.split("_")[1]
                            check_labels.append(f"Panel {panel_num} content incorrect")
                        elif "borders" in check:
                            check_labels.append("Visible borders between panels - need cleaner split-screen")
                    all_feedback_parts.append("PANEL ISSUES: " + "; ".join(check_labels))

                if panel_issues:
                    all_feedback_parts.append("SPECIFIC ISSUES: " + "; ".join(panel_issues))

                if feedback.strip():
                    all_feedback_parts.append("USER FEEDBACK: " + feedback.strip())

                combined_feedback = " | ".join(all_feedback_parts)

                if combined_feedback:
                    # Try Claude API for improvement
                    with st.spinner("🤖 Using Claude AI to improve prompt..."):
                        improved_prompt, best_practice = call_claude_for_prompt_improvement(
                            st.session_state.prompt,
                            combined_feedback,
                            failed_panel_checks
                        )

                    if improved_prompt:
                        st.session_state.prompt = improved_prompt
                        st.session_state.prompt_updated_notice = "Prompt improved by Claude AI based on panel issues!"
                        if best_practice:
                            bp_data = load_best_practices()
                            bp_data["practices"].append({
                                "lesson": best_practice,
                                "date": datetime.now().isoformat(),
                                "feedback": combined_feedback,
                                "stage": "panel_splitting"
                            })
                            save_best_practices(bp_data)
                    else:
                        st.session_state.prompt = incorporate_feedback_into_prompt(
                            st.session_state.prompt,
                            f"PANEL SPLITTING ISSUES: {combined_feedback}"
                        )
                        st.session_state.prompt_updated_notice = "Feedback appended to prompt (Claude API unavailable)."

                    # Store in session history
                    if "prompt_improvements" not in st.session_state:
                        st.session_state.prompt_improvements = []
                    st.session_state.prompt_improvements.append({
                        "type": "Panel Splitting Feedback",
                        "feedback": combined_feedback,
                        "failed_checks": failed_panel_checks,
                        "best_practice": best_practice if 'best_practice' in dir() and best_practice else None
                    })

                # Clear images and go back to step 3
                st.session_state.storyboard_image = None
                st.session_state.panel_images = []
                log_feedback("split", combined_feedback, "regenerate")
                st.session_state.step = 3
                st.rerun()
        with col4:
            can_proceed = "No borders" in has_borders and len(failed_panel_checks) == 0
            if st.button("✅ Approve & Upscale", type="primary", disabled=not can_proceed):
                log_feedback("split", feedback, "approved")
                st.session_state.step = 5
                st.rerun()
            if not can_proceed:
                st.caption("Fix all issues first")

    else:
        # Need to split
        st.info("Split the storyboard into 4 individual panels.")

        if st.session_state.storyboard_image:
            st.image(st.session_state.storyboard_image, caption="Storyboard to split", use_container_width=True)

        margin_pct = st.slider("Border margin to remove (%)", 0, 15, 4, key="margin_slider")

        st.info(f"Will remove {margin_pct}% from each panel edge to eliminate borders")

        if st.button("✂️ Split into Panels", type="primary"):
            with st.spinner("Splitting panels..."):
                img = st.session_state.storyboard_image
                width, height = img.size

                panel_w = width // 2
                panel_h = height // 2
                margin = int(min(panel_w, panel_h) * margin_pct / 100)

                panels = []
                for i, (row, col) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
                    x1 = col * panel_w + margin
                    y1 = row * panel_h + margin
                    x2 = (col + 1) * panel_w - margin
                    y2 = (row + 1) * panel_h - margin

                    panel = img.crop((x1, y1, x2, y2))
                    panels.append(panel)

                st.session_state.panel_images = panels
                st.success("✅ Panels extracted!")
                st.rerun()


# ============================================================================
# STEP 5: UPSCALING
# ============================================================================
elif st.session_state.step == 5:
    st.header("Step 5: Upscaling Panels")

    # Get selected panels from previous step
    selected_panels = st.session_state.get("selected_panels", [True] * 4)
    selected_indices = [i for i, sel in enumerate(selected_panels) if sel]

    if "upscaled_images" in st.session_state and st.session_state.upscaled_images:
        st.success("✅ Panels upscaled!")

        # Initialize video selection if not exists
        if "panels_for_video" not in st.session_state:
            st.session_state.panels_for_video = [True] * len(st.session_state.upscaled_images)

        st.subheader("🎬 Select Panels for Video Generation")
        st.info("Uncheck panels you don't want to generate videos for")

        cols = st.columns(2)
        for i, up_img in enumerate(st.session_state.upscaled_images):
            original_panel_num = st.session_state.upscaled_panel_indices[i] + 1
            with cols[i % 2]:
                st.image(up_img, caption=f"Panel {original_panel_num}", use_container_width=True)
                st.caption(f"Size: {up_img.size[0]}x{up_img.size[1]}")
                # Checkbox to select for video generation
                st.session_state.panels_for_video[i] = st.checkbox(
                    f"🎬 Generate video for Panel {original_panel_num}",
                    value=st.session_state.panels_for_video[i],
                    key=f"video_select_{i}"
                )

        # Show selection summary
        video_count = sum(st.session_state.panels_for_video)
        st.info(f"📊 {video_count} panels selected for video generation")

        feedback = st.text_area("Feedback on upscaled panels:", key="upscale_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Split"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button("🔄 Re-upscale"):
                st.session_state.upscaled_images = []
                if "panels_for_video" in st.session_state:
                    del st.session_state.panels_for_video
                st.rerun()
        with col3:
            can_proceed = video_count > 0
            if st.button("✅ Approve & Create Video Prompts", type="primary", disabled=not can_proceed):
                log_feedback("upscale", feedback, "approved")
                st.session_state.step = 6
                st.rerun()
            if not can_proceed:
                st.caption("Select at least 1 panel")

    else:
        st.info("Upscale selected panels using LANCZOS resampling (content-preserving, no AI regeneration).")

        # Show only selected panels
        if st.session_state.panel_images and selected_indices:
            st.write(f"**{len(selected_indices)} panels selected for upscaling:**")
            cols = st.columns(min(4, len(selected_indices)))
            for col_idx, panel_idx in enumerate(selected_indices):
                panel = st.session_state.panel_images[panel_idx]
                with cols[col_idx % len(cols)]:
                    st.image(panel, caption=f"Panel {panel_idx + 1}\n{panel.size[0]}x{panel.size[1]}", use_container_width=True)
        elif not selected_indices:
            st.warning("⚠️ No panels selected! Go back and select at least one panel.")

        scale = st.selectbox("Upscale factor", [2, 3, 4], index=0, key="scale_select")

        if st.session_state.panel_images and selected_indices:
            original_size = st.session_state.panel_images[selected_indices[0]].size
            new_size = (original_size[0] * scale, original_size[1] * scale)
            st.info(f"Will upscale from {original_size[0]}x{original_size[1]} to {new_size[0]}x{new_size[1]}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Split"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button("⬆️ Upscale Selected Panels", type="primary", disabled=not selected_indices):
                with st.spinner("Upscaling panels..."):
                    upscaled = []
                    upscaled_indices = []
                    for panel_idx in selected_indices:
                        panel = st.session_state.panel_images[panel_idx]
                        new_size = (panel.size[0] * scale, panel.size[1] * scale)
                        up_img = panel.resize(new_size, Image.LANCZOS)
                        upscaled.append(up_img)
                        upscaled_indices.append(panel_idx)

                    st.session_state.upscaled_images = upscaled
                    st.session_state.upscaled_panel_indices = upscaled_indices
                    st.session_state.panels_for_video = [True] * len(upscaled)
                    st.success("✅ Upscaling complete!")
                    st.rerun()


# ============================================================================
# STEP 6: VIDEO PROMPTS
# ============================================================================
elif st.session_state.step == 6:
    st.header("Step 6: Video Motion Prompts")

    # Get panels selected for video generation
    panels_for_video = st.session_state.get("panels_for_video", [])
    upscaled_indices = st.session_state.get("upscaled_panel_indices", [])
    selected_for_video = [(i, idx) for i, (sel, idx) in enumerate(zip(panels_for_video, upscaled_indices)) if sel]

    st.info(f"Generate and review motion prompts for {len(selected_for_video)} selected panels.")

    # Define scene actions based on original panel numbers
    scene_actions = {
        0: f"{st.session_state.pokemon[0]} launching attack, fire streaming from mouth",
        1: f"{st.session_state.pokemon[1]} being hit, reacting to impact, body recoiling",
        2: f"{st.session_state.pokemon[1]} charging counter-attack, energy gathering at mouth",
        3: f"{st.session_state.pokemon[1]} releasing attack beam toward {st.session_state.pokemon[0]}"
    }

    # Show selected upscaled panels for reference
    st.subheader("📸 Panels Selected for Video Generation")
    if "upscaled_images" in st.session_state and selected_for_video:
        num_cols = min(4, len(selected_for_video))
        cols = st.columns(num_cols)
        for col_idx, (img_idx, panel_idx) in enumerate(selected_for_video):
            with cols[col_idx % num_cols]:
                st.image(st.session_state.upscaled_images[img_idx], caption=f"Panel {panel_idx + 1}", use_container_width=True)

    # Generate or edit video prompts only for selected panels
    st.subheader("🎬 Motion Prompts for Selected Panels")

    video_prompts = {}
    prompt_validations = []

    for img_idx, panel_idx in selected_for_video:
        panel_num = panel_idx + 1
        with st.expander(f"Panel {panel_num} Motion Prompt", expanded=True):
            # Generate if not exists
            existing_prompts = st.session_state.get("video_prompts", {})
            if panel_idx not in existing_prompts:
                pokemon_name = st.session_state.pokemon[0] if panel_idx == 0 else st.session_state.pokemon[1]
                default_prompt = validator.generate_holistic_video_prompt(
                    pokemon_name=pokemon_name,
                    action=scene_actions.get(panel_idx, "battle action"),
                    scene_context=f"volcanic battlefield, {st.session_state.environment} environment"
                )
            else:
                default_prompt = existing_prompts[panel_idx]

            edited = st.text_area(
                f"Motion prompt for Panel {panel_num}",
                value=default_prompt,
                height=100,
                key=f"video_prompt_{panel_idx}"
            )
            video_prompts[panel_idx] = edited

            # Validate
            validation = validator.validate_video_prompt(edited)
            prompt_validations.append(validation)

            col1, col2 = st.columns(2)
            with col1:
                if validation.passed:
                    st.success(f"✅ Valid (Score: {validation.score:.2f})")
                else:
                    st.error(f"❌ Invalid (Score: {validation.score:.2f})")
            with col2:
                if validation.issues:
                    st.warning(", ".join(validation.issues))

    st.session_state.video_prompts = video_prompts

    # Overall validation
    all_valid = all(v.passed for v in prompt_validations) if prompt_validations else False

    if all_valid:
        st.success("✅ All video prompts are valid!")
    elif not selected_for_video:
        st.warning("⚠️ No panels selected for video generation. Go back and select panels.")
    else:
        st.error("❌ Some video prompts have issues. Fix them before generating videos.")

    feedback = st.text_area("Final feedback before video generation:", key="video_feedback")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Upscale"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("💾 Save Configuration"):
            # Create downloadable config
            config = {
                "pokemon": st.session_state.pokemon,
                "environment": st.session_state.environment,
                "prompt": st.session_state.prompt,
                "negative_prompt": st.session_state.negative_prompt,
                "video_prompts": st.session_state.video_prompts,
                "feedback_log": st.session_state.feedback_log
            }
            config_json = json.dumps(config, indent=2)
            st.download_button(
                "📥 Download Config JSON",
                config_json,
                file_name="pokemon_studio_config.json",
                mime="application/json"
            )

    with col3:
        st.warning("⚠️ Video generation uses API credits!")
        if st.button("🎬 Generate Videos", type="primary", disabled=not all_valid):
            log_feedback("video_prompts", feedback, "approved_for_generation")
            st.success("✅ Ready for video generation!")
            st.balloons()
            st.info("Video generation would proceed here. Implementation coming soon!")


# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.header("📋 Session Info")
    st.write(f"**Current Step:** {st.session_state.step}/6")

    if hasattr(st.session_state, 'pokemon') and st.session_state.pokemon:
        st.write(f"**Pokemon:** {' vs '.join(st.session_state.pokemon)}")
        st.write(f"**Environment:** {st.session_state.get('environment', 'N/A')}")

    st.divider()

    # API Key Status
    st.header("🔑 API Status")
    if KIE_API_KEY:
        st.success(f"KIE: ✅ {KIE_API_KEY[:8]}...")
    else:
        st.error("KIE: ❌ Not found")

    if ANTHROPIC_API_KEY:
        st.success(f"Claude: ✅ {ANTHROPIC_API_KEY[:10]}...")
    else:
        st.error("Claude: ❌ Not found")
        st.caption("Add ANTHROPIC_API_KEY to .env file")

    st.divider()

    # Validation Status
    st.header("🔍 Validation Status")
    if st.session_state.validation_errors:
        st.error(f"{len(st.session_state.validation_errors)} issues found")
        for err in st.session_state.validation_errors[:3]:
            st.caption(f"• {err}")
    else:
        st.success("No validation errors")

    st.divider()

    st.header("📝 Feedback Log")
    for log in st.session_state.feedback_log[-5:]:
        st.write(f"• **{log['step']}**: {log['action']}")
        if log['feedback']:
            st.caption(log['feedback'][:50])

    st.divider()

    if st.button("🔄 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.divider()
    st.caption("Pokemon AI Video Studio v2.0")
    st.caption("With validation & feedback")
