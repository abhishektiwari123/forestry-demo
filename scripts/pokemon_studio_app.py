#!/usr/bin/env python3
"""
Pokemon AI Video Generator Studio - Interactive Web UI

A step-by-step interactive workflow for generating Pokemon battle videos.
Each step requires manual approval before proceeding.

Run with: streamlit run scripts/pokemon_studio_app.py
"""

import streamlit as st
import subprocess
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
if "panels" not in st.session_state:
    st.session_state.panels = []
if "video_prompts" not in st.session_state:
    st.session_state.video_prompts = []
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []
if "output_dir" not in st.session_state:
    st.session_state.output_dir = f"studio_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Load API key
def get_api_key():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("KIE_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return os.environ.get("KIE_API_KEY", "")

KIE_API_KEY = get_api_key()

# Create validator
validator = PromptValidator()


def log_feedback(step: str, feedback: str, action: str):
    """Log user feedback for each step."""
    st.session_state.feedback_log.append({
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "feedback": feedback,
        "action": action
    })


def call_kie_api(endpoint: str, payload: dict = None, method: str = "GET"):
    """Call KIE API with error handling."""
    base_url = "https://api.kieai.erweima.ai/api/v1"

    if method == "POST":
        curl_cmd = [
            "curl", "-k", "-s", "-X", "POST",
            f"{base_url}/{endpoint}",
            "-H", f"Authorization: Bearer {KIE_API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]
    else:
        curl_cmd = [
            "curl", "-k", "-s",
            f"{base_url}/{endpoint}",
            "-H", f"Authorization: Bearer {KIE_API_KEY}"
        ]

    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=60)
    return json.loads(result.stdout) if result.stdout else {}


def download_file(url: str, output_path: str) -> bool:
    """Download file from URL."""
    curl_cmd = ["curl", "-k", "-L", "-s", "-o", output_path, url]
    result = subprocess.run(curl_cmd, capture_output=True, timeout=120)
    return result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000


# ============================================================================
# HEADER
# ============================================================================
st.title("🐉 Pokemon AI Video Studio")
st.markdown("**Interactive step-by-step workflow for Pokemon battle video generation**")

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

        st.subheader("Output Directory")
        st.text_input("Output folder", value=st.session_state.output_dir, key="output_dir_input")

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
        os.makedirs(st.session_state.output_dir, exist_ok=True)
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
    st.subheader("Prompt Validation")
    validation = validator.validate_storyboard_prompt(
        edited_prompt,
        panel_count=4,
        pokemon_names=st.session_state.pokemon
    )

    if validation.passed:
        st.success(f"✅ Validation PASSED (Score: {validation.score:.2f})")
    else:
        st.warning(f"⚠️ Validation Score: {validation.score:.2f}")

    if validation.issues:
        st.error("Issues: " + ", ".join(validation.issues))
    if validation.warnings:
        st.warning("Warnings: " + ", ".join(validation.warnings))
    if validation.suggestions:
        st.info("Suggestions: " + ", ".join(validation.suggestions))

    # Checklist
    st.subheader("Manual Checklist")
    check1 = st.checkbox(f"{st.session_state.pokemon[0]} positioned on LEFT, facing RIGHT")
    check2 = st.checkbox(f"{st.session_state.pokemon[1]} positioned on RIGHT, facing LEFT")
    check3 = st.checkbox("Attack effects explicitly described (VISIBLE beams)")
    check4 = st.checkbox("Battle damage continuity mentioned for panels 3-4")
    check5 = st.checkbox("Photorealistic style enforced (no anime/cartoon)")

    # Feedback
    st.subheader("Your Feedback")
    feedback = st.text_area("Add notes/feedback about this prompt:", key="prompt_feedback")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Setup"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🔄 Regenerate Prompt"):
            st.session_state.prompt = ""
            st.rerun()
    with col3:
        if st.button("✅ Approve & Generate Image", type="primary"):
            st.session_state.prompt = edited_prompt
            log_feedback("prompt", feedback, "approved")
            st.session_state.step = 3
            st.rerun()


# ============================================================================
# STEP 3: IMAGE GENERATION
# ============================================================================
elif st.session_state.step == 3:
    st.header("Step 3: Storyboard Image Generation")

    if st.session_state.storyboard_path and os.path.exists(st.session_state.storyboard_path):
        # Already generated - show result
        st.success("✅ Storyboard generated!")
        st.image(st.session_state.storyboard_path, caption="Generated Storyboard")

        # Analysis
        img = Image.open(st.session_state.storyboard_path)
        st.write(f"Image size: {img.size[0]}x{img.size[1]}")
        st.write(f"Aspect ratio: {img.size[0]/img.size[1]:.2f}")

        # Manual review
        st.subheader("Manual Review Checklist")
        st.markdown(f"""
        Review the generated storyboard:
        - [ ] **Panel 1 (top-left)**: {st.session_state.pokemon[0]} attacking, visible beam?
        - [ ] **Panel 2 (top-right)**: Impact on {st.session_state.pokemon[1]}?
        - [ ] **Panel 3 (bottom-left)**: {st.session_state.pokemon[1]} shows damage, charging attack?
        - [ ] **Panel 4 (bottom-right)**: Counter-attack with damage continuity?
        - [ ] Both Pokemon facing each other in all panels?
        - [ ] Photorealistic style (not anime/cartoon)?
        """)

        # Feedback
        feedback = st.text_area("Feedback on generated image:", key="image_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Prompt"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("🔄 Regenerate Image"):
                st.session_state.storyboard_path = None
                st.rerun()
        with col3:
            if st.button("✅ Approve & Split Panels", type="primary"):
                log_feedback("image", feedback, "approved")
                st.session_state.step = 4
                st.rerun()

    else:
        # Need to generate
        st.info("Click below to generate the storyboard image from your approved prompt.")

        with st.expander("View Prompt"):
            st.text(st.session_state.prompt[:500] + "...")

        if st.button("🎨 Generate Storyboard", type="primary"):
            with st.spinner("Generating storyboard... This may take 30-60 seconds"):
                # Submit generation request
                payload = {
                    "model": "nano-banana-pro",
                    "prompt": st.session_state.prompt,
                    "negativePrompt": st.session_state.negative_prompt,
                    "imageCount": 1,
                    "imageAspect": "16:9"
                }

                response = call_kie_api("generate", payload, method="POST")
                task_id = response.get("data", {}).get("taskId")

                if not task_id:
                    st.error(f"Failed to submit generation task: {response}")
                else:
                    st.write(f"Task ID: {task_id}")
                    progress = st.progress(0)

                    # Poll for completion
                    for i in range(60):
                        time.sleep(5)
                        progress.progress((i + 1) / 60)

                        status = call_kie_api(f"recordInfo?taskId={task_id}")
                        state = status.get("data", {}).get("state", "").lower()

                        if state == "success":
                            result_json = status.get("data", {}).get("resultJson", "{}")
                            if isinstance(result_json, str):
                                result_json = json.loads(result_json)

                            urls = result_json.get("resultUrls", [])
                            if urls:
                                output_path = os.path.join(st.session_state.output_dir, "storyboard.jpg")
                                if download_file(urls[0], output_path):
                                    st.session_state.storyboard_path = output_path
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

    if st.session_state.panels:
        # Already split - show panels
        st.success("✅ Panels extracted!")

        cols = st.columns(2)
        for i, panel_path in enumerate(st.session_state.panels):
            with cols[i % 2]:
                st.image(panel_path, caption=f"Panel {i+1}")
                img = Image.open(panel_path)
                st.caption(f"Size: {img.size[0]}x{img.size[1]}")

        # Manual review
        st.subheader("Panel-by-Panel Review")
        reviews = []
        for i in range(4):
            with st.expander(f"Panel {i+1} Review"):
                ok = st.checkbox(f"Panel {i+1} looks correct", key=f"panel_{i}_ok")
                notes = st.text_input(f"Notes for Panel {i+1}", key=f"panel_{i}_notes")
                reviews.append({"ok": ok, "notes": notes})

        # Check for frame borders
        st.subheader("Border Check")
        has_borders = st.radio(
            "Are there visible frame borders in any panel?",
            ["No borders visible", "Some borders visible", "Heavy borders visible"]
        )

        feedback = st.text_area("Overall feedback on panel splitting:", key="split_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Image"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("🔄 Re-split with Different Margins"):
                st.session_state.panels = []
                st.rerun()
        with col3:
            if st.button("✅ Approve & Upscale", type="primary"):
                log_feedback("split", feedback, "approved")
                st.session_state.step = 5
                st.rerun()

    else:
        # Need to split
        st.info("Split the storyboard into 4 individual panels.")

        if st.session_state.storyboard_path:
            st.image(st.session_state.storyboard_path, caption="Storyboard to split")

        margin_pct = st.slider("Border margin to remove (%)", 0, 15, 4)

        if st.button("✂️ Split into Panels", type="primary"):
            with st.spinner("Splitting panels..."):
                img = Image.open(st.session_state.storyboard_path)
                width, height = img.size

                panel_w = width // 2
                panel_h = height // 2
                margin = int(min(panel_w, panel_h) * margin_pct / 100)

                panels_dir = os.path.join(st.session_state.output_dir, "panels")
                os.makedirs(panels_dir, exist_ok=True)

                panels = []
                for i, (row, col) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
                    x1 = col * panel_w + margin
                    y1 = row * panel_h + margin
                    x2 = (col + 1) * panel_w - margin
                    y2 = (row + 1) * panel_h - margin

                    panel = img.crop((x1, y1, x2, y2))
                    panel_path = os.path.join(panels_dir, f"panel_{i+1}.jpg")
                    panel.save(panel_path, "JPEG", quality=95)
                    panels.append(panel_path)

                st.session_state.panels = panels
                st.success("✅ Panels extracted!")
                st.rerun()


# ============================================================================
# STEP 5: UPSCALING
# ============================================================================
elif st.session_state.step == 5:
    st.header("Step 5: Upscaling Panels")

    upscaled_dir = os.path.join(st.session_state.output_dir, "upscaled")

    # Check if already upscaled
    upscaled_files = []
    if os.path.exists(upscaled_dir):
        upscaled_files = [os.path.join(upscaled_dir, f) for f in sorted(os.listdir(upscaled_dir)) if f.endswith('.jpg')]

    if len(upscaled_files) == 4:
        st.success("✅ Panels upscaled!")

        cols = st.columns(2)
        for i, up_path in enumerate(upscaled_files):
            with cols[i % 2]:
                st.image(up_path, caption=f"Upscaled Panel {i+1}")
                img = Image.open(up_path)
                st.caption(f"Size: {img.size[0]}x{img.size[1]}")

        feedback = st.text_area("Feedback on upscaled panels:", key="upscale_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⬅️ Back to Split"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button("🔄 Re-upscale"):
                import shutil
                shutil.rmtree(upscaled_dir, ignore_errors=True)
                st.rerun()
        with col3:
            if st.button("✅ Approve & Create Video Prompts", type="primary"):
                log_feedback("upscale", feedback, "approved")
                st.session_state.step = 6
                st.rerun()

    else:
        st.info("Upscale panels using LANCZOS resampling (content-preserving).")

        scale = st.selectbox("Upscale factor", [2, 3, 4], index=0)

        if st.button("⬆️ Upscale Panels", type="primary"):
            with st.spinner("Upscaling panels..."):
                os.makedirs(upscaled_dir, exist_ok=True)

                for i, panel_path in enumerate(st.session_state.panels):
                    img = Image.open(panel_path)
                    new_size = (img.size[0] * scale, img.size[1] * scale)
                    upscaled = img.resize(new_size, Image.LANCZOS)

                    up_path = os.path.join(upscaled_dir, f"scene_{i+1:02d}.jpg")
                    upscaled.save(up_path, "JPEG", quality=95)

                st.success("✅ Upscaling complete!")
                st.rerun()


# ============================================================================
# STEP 6: VIDEO PROMPTS
# ============================================================================
elif st.session_state.step == 6:
    st.header("Step 6: Video Motion Prompts")

    st.info("Generate motion prompts for each panel to create videos.")

    # Define scene actions
    scene_actions = [
        f"{st.session_state.pokemon[0]} launching attack, fire streaming from mouth",
        f"{st.session_state.pokemon[1]} being hit, reacting to impact, body recoiling",
        f"{st.session_state.pokemon[1]} charging counter-attack, energy gathering at mouth",
        f"{st.session_state.pokemon[1]} releasing attack beam toward {st.session_state.pokemon[0]}"
    ]

    # Generate or edit video prompts
    st.subheader("Motion Prompts for Each Scene")

    video_prompts = []
    for i in range(4):
        with st.expander(f"Scene {i+1} Motion Prompt", expanded=True):
            # Generate if not exists
            if len(st.session_state.video_prompts) <= i:
                pokemon_name = st.session_state.pokemon[0] if i in [0, 3] else st.session_state.pokemon[1]
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
            if validation.passed:
                st.success(f"✅ Valid (Score: {validation.score:.2f})")
            else:
                st.warning(f"⚠️ Score: {validation.score:.2f}")
                if validation.issues:
                    st.error(", ".join(validation.issues))

    st.session_state.video_prompts = video_prompts

    feedback = st.text_area("Final feedback before video generation:", key="video_feedback")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Upscale"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("💾 Save Configuration"):
            # Save all config
            config = {
                "pokemon": st.session_state.pokemon,
                "environment": st.session_state.environment,
                "prompt": st.session_state.prompt,
                "negative_prompt": st.session_state.negative_prompt,
                "video_prompts": st.session_state.video_prompts,
                "feedback_log": st.session_state.feedback_log
            }
            config_path = os.path.join(st.session_state.output_dir, "config.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            st.success(f"Saved to {config_path}")

    with col3:
        st.warning("⚠️ Video generation uses credits!")
        if st.button("🎬 Generate Videos", type="primary"):
            log_feedback("video_prompts", feedback, "approved_for_generation")
            st.success("Ready for video generation!")
            st.info("Video generation would proceed here (disabled to save credits)")


# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.header("📋 Session Info")
    st.write(f"**Current Step:** {st.session_state.step}/6")
    st.write(f"**Output Dir:** {st.session_state.output_dir}")

    if hasattr(st.session_state, 'pokemon'):
        st.write(f"**Pokemon:** {' vs '.join(st.session_state.pokemon)}")

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
    st.caption("Pokemon AI Video Studio v1.0")
    st.caption("Storyboard-only mode (videos disabled)")
