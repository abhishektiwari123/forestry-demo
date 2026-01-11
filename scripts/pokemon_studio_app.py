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

KIE_API_KEY = get_api_key()

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

    # Generate prompt if not already done
    if not st.session_state.prompt:
        prompt, negative_prompt = validator.generate_holistic_storyboard_prompt(
            pokemon_names=st.session_state.pokemon,
            scene_type="battle",
            environment=st.session_state.environment,
            panel_count=4
        )
        st.session_state.prompt = prompt
        st.session_state.negative_prompt = negative_prompt

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

    # Incorporate Feedback Button
    if feedback.strip():
        if st.button("🔄 Incorporate Feedback into Prompt", type="secondary"):
            st.session_state.prompt = incorporate_feedback_into_prompt(edited_prompt, feedback)
            st.session_state.user_feedback = ""  # Clear feedback after incorporating
            st.success("Feedback incorporated! Review the updated prompt above.")
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
        feedback = st.text_area(
            "What needs to be fixed?",
            key="image_feedback",
            placeholder="e.g., 'Dragonite is facing away', 'No attack beam visible in panel 1', 'Style looks like anime'"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Prompt"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("🔄 Regenerate with Feedback"):
                if feedback.strip():
                    st.session_state.prompt = incorporate_feedback_into_prompt(
                        st.session_state.prompt,
                        f"PREVIOUS IMAGE ISSUES: {feedback}"
                    )
                st.session_state.storyboard_image = None
                log_feedback("image", feedback, "regenerate")
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
                # Submit generation request
                payload = {
                    "model": "nano-banana-pro",
                    "prompt": st.session_state.prompt,
                    "negativePrompt": st.session_state.negative_prompt,
                    "imageCount": 1,
                    "imageAspect": "16:9"
                }

                response = call_kie_api("playground/createTask", payload, method="POST")

                # Check for None or error response
                if response is None:
                    st.error("API Error: No response from server")
                    st.warning("💡 The API is not accessible. Click **Use Demo Mode** to test the workflow with sample images.")
                elif "error" in response:
                    st.error(f"API Error: {response['error']}")
                    st.warning("💡 The API is not accessible. Click **Use Demo Mode** to test the workflow with sample images.")
                elif response.get("code") != 200:
                    st.error(f"API Error: {response.get('message', 'Unknown error')} (Code: {response.get('code')})")
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

                            status = call_kie_api(f"playground/recordInfo?taskId={task_id}")

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

        cols = st.columns(2)
        for i, panel_img in enumerate(st.session_state.panel_images):
            with cols[i % 2]:
                st.image(panel_img, caption=f"Panel {i+1}", use_container_width=True)
                st.caption(f"Size: {panel_img.size[0]}x{panel_img.size[1]}")

        # Panel-by-panel validation
        st.subheader("🔍 Panel Validation")

        panel_issues = []
        for i in range(4):
            with st.expander(f"Panel {i+1} Review", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    ok = st.checkbox(f"Panel {i+1} content correct", key=f"panel_{i}_ok")
                with col2:
                    border_ok = st.checkbox(f"No visible borders/edges", key=f"panel_{i}_border")

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

        feedback = st.text_area("Overall feedback on panel splitting:", key="split_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Image"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("🔄 Re-split with Different Margins"):
                st.session_state.panel_images = []
                st.rerun()
        with col3:
            can_proceed = "No borders" in has_borders
            if st.button("✅ Approve & Upscale", type="primary", disabled=not can_proceed):
                log_feedback("split", feedback, "approved")
                st.session_state.step = 5
                st.rerun()

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

    if "upscaled_images" in st.session_state and st.session_state.upscaled_images:
        st.success("✅ Panels upscaled!")

        cols = st.columns(2)
        for i, up_img in enumerate(st.session_state.upscaled_images):
            with cols[i % 2]:
                st.image(up_img, caption=f"Upscaled Panel {i+1}", use_container_width=True)
                st.caption(f"Size: {up_img.size[0]}x{up_img.size[1]}")

        feedback = st.text_area("Feedback on upscaled panels:", key="upscale_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Split"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button("🔄 Re-upscale"):
                st.session_state.upscaled_images = []
                st.rerun()
        with col3:
            if st.button("✅ Approve & Create Video Prompts", type="primary"):
                log_feedback("upscale", feedback, "approved")
                st.session_state.step = 6
                st.rerun()

    else:
        st.info("Upscale panels using LANCZOS resampling (content-preserving, no AI regeneration).")

        # Show current panels
        if st.session_state.panel_images:
            cols = st.columns(4)
            for i, panel in enumerate(st.session_state.panel_images):
                with cols[i]:
                    st.image(panel, caption=f"Panel {i+1}\n{panel.size[0]}x{panel.size[1]}", use_container_width=True)

        scale = st.selectbox("Upscale factor", [2, 3, 4], index=0, key="scale_select")

        if st.session_state.panel_images:
            original_size = st.session_state.panel_images[0].size
            new_size = (original_size[0] * scale, original_size[1] * scale)
            st.info(f"Will upscale from {original_size[0]}x{original_size[1]} to {new_size[0]}x{new_size[1]}")

        if st.button("⬆️ Upscale Panels", type="primary"):
            with st.spinner("Upscaling panels..."):
                upscaled = []
                for panel in st.session_state.panel_images:
                    new_size = (panel.size[0] * scale, panel.size[1] * scale)
                    up_img = panel.resize(new_size, Image.LANCZOS)
                    upscaled.append(up_img)

                st.session_state.upscaled_images = upscaled
                st.success("✅ Upscaling complete!")
                st.rerun()


# ============================================================================
# STEP 6: VIDEO PROMPTS
# ============================================================================
elif st.session_state.step == 6:
    st.header("Step 6: Video Motion Prompts")

    st.info("Generate and review motion prompts for each panel before creating videos.")

    # Define scene actions
    scene_actions = [
        f"{st.session_state.pokemon[0]} launching attack, fire streaming from mouth",
        f"{st.session_state.pokemon[1]} being hit, reacting to impact, body recoiling",
        f"{st.session_state.pokemon[1]} charging counter-attack, energy gathering at mouth",
        f"{st.session_state.pokemon[1]} releasing attack beam toward {st.session_state.pokemon[0]}"
    ]

    # Show upscaled panels for reference
    st.subheader("📸 Reference Panels")
    if "upscaled_images" in st.session_state:
        cols = st.columns(4)
        for i, img in enumerate(st.session_state.upscaled_images):
            with cols[i]:
                st.image(img, caption=f"Scene {i+1}", use_container_width=True)

    # Generate or edit video prompts
    st.subheader("🎬 Motion Prompts for Each Scene")

    video_prompts = []
    prompt_validations = []

    for i in range(4):
        with st.expander(f"Scene {i+1} Motion Prompt", expanded=True):
            # Generate if not exists
            if len(st.session_state.video_prompts) <= i:
                pokemon_name = st.session_state.pokemon[0] if i in [0] else st.session_state.pokemon[1]
                if i == 3:
                    pokemon_name = st.session_state.pokemon[1]  # Dragonite attacks in scene 4
                default_prompt = validator.generate_holistic_video_prompt(
                    pokemon_name=pokemon_name,
                    action=scene_actions[i],
                    scene_context=f"volcanic battlefield, {st.session_state.environment} environment"
                )
            else:
                default_prompt = st.session_state.video_prompts[i]

            edited = st.text_area(
                f"Motion prompt for Scene {i+1}",
                value=default_prompt,
                height=100,
                key=f"video_prompt_{i}"
            )
            video_prompts.append(edited)

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
    all_valid = all(v.passed for v in prompt_validations)

    if all_valid:
        st.success("✅ All video prompts are valid!")
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
