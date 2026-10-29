import streamlit as st
import os
import subprocess
import json
from services.gemini_service import generate_nursery_content
from services.ffmpeg_stitcher import assemble_video
from services.veo_service import generate_scene_video

# Setup working directories
ASSETS_DIR = "pipeline_output"
os.makedirs(ASSETS_DIR, exist_ok=True)

st.set_page_config(page_title="Super Kidz AI - Studio Hub", layout="wide")
st.title("Super Kidz AI - Automated Video Studio")

# -------------------------------------------------------------
# STEP 1: CONTENT CONFIGURATION & CRITERIA FORM
# -------------------------------------------------------------
with st.expander("Story & Video Generation Criteria", expanded=True):
    with st.form("criteria_form"):
        col1, col2, col3 = st.columns([1.5, 1.5, 1])

        with col1:
            st.markdown("**Character & Story Setup**")
            character_type = st.selectbox(
                "Primary Character Category",
                ["Domestic Animal (Dog, Cat)", "Farm Animal", "Dancing Fruits & Veggies", "Vehicles / Objects"]
            )
            character_description = st.text_input(
                "Character Details",
                value="Fluffy golden puppy with big curious eyes and a blue collar"
            )
            base_story = st.text_area(
                "Base Storyline / Core Action",
                value="The puppy plays in front of a blue house, drinks water in the kitchen, jumps on the couch with a ball, and curls up to sleep.",
                height=100
            )

        with col2:
            st.markdown("**Format & Animation Style**")
            video_type = st.radio(
                "Video Format",
                ["YouTube Shorts (9:16 Vertical)", "Standard Long-form (16:9 Landscape)"],
                index=0
            )
            visual_style = st.selectbox(
                "Animation Style",
                ["Pixar 3D Stylized (Soft Studio Lighting)", "Claymation 3D", "Vibrant Cartoon Flat 2D", "Watercolor Storybook"]
            )
            target_duration = st.select_slider(
                "Target Duration",
                options=["30s (Short)", "60s (Medium Short)", "90s (Extended Nursery Rhyme)"],
                value="90s (Extended Nursery Rhyme)"
            )

        with col3:
            st.markdown("**Music & Mood Parameters**")
            mood = st.selectbox(
                "Song Vibe",
                ["Upbeat & Bouncy (Toddler Dance)", "Educational & Catchy", "Gentle Bedtime Lullaby"]
            )
            tempo_bpm = st.slider("BPM (Tempo)", min_value=90, max_value=130, value=110)
            scene_count = st.number_input("Number of Scenes", min_value=2, max_value=8, value=4)

        submit_criteria = st.form_submit_button("Generate Lyrics & Visual Prompts", type="primary")

# -------------------------------------------------------------
# STEP 2: SCRIPT & PROMPT GENERATION
# -------------------------------------------------------------
if submit_criteria:
    aspect_ratio = "9:16 vertical" if "9:16" in video_type else "16:9 widescreen"
    
    st.session_state["config"] = {
        "character": character_description,
        "story": base_story,
        "aspect_ratio": aspect_ratio,
        "style": visual_style,
        "bpm": tempo_bpm,
        "scene_count": int(scene_count)
    }

    with st.spinner("Generating lyrics and cinematic visual prompts via Gemini..."):
        try:
            result = generate_nursery_content(
                character_type=character_type,
                character_desc=character_description,
                base_story=base_story,
                visual_style=visual_style,
                aspect_ratio=aspect_ratio,
                mood=mood,
                bpm=tempo_bpm,
                scene_count=int(scene_count)
            )

            st.session_state["lyrics"] = result["lyrics"]
            st.session_state["prompts"] = result["scene_prompts"]
            st.session_state["title"] = result["suggested_title"]
            st.success(f"✨ Generated: {result['suggested_title']}")
        except Exception as e:
            st.error(f"Gemini API Error: {e}")

# -------------------------------------------------------------
# STEP 3: HUMAN VERIFICATION & PROMPT EDITING
# -------------------------------------------------------------
if "lyrics" in st.session_state:
    st.divider()
    st.subheader("Review & Edit Prompts")
    
    col_lyric, col_prompts = st.columns([1, 1.2])
    with col_lyric:
        st.session_state["lyrics"] = st.text_area(
            "Song Lyrics (Copy into Suno AI)", 
            st.session_state["lyrics"], 
            height=260
        )
    
    with col_prompts:
        updated_prompts = []
        for i in range(st.session_state["config"]["scene_count"]):
            prompt_val = st.session_state["prompts"][i] if i < len(st.session_state["prompts"]) else ""
            p = st.text_input(f"Scene {i+1} Visual Prompt (Copy into Google Flow / Veo)", value=prompt_val, key=f"p_{i}")
            updated_prompts.append(p)
        st.session_state["prompts"] = updated_prompts

# -------------------------------------------------------------
# STEP 4: ASSET VERIFICATION (AUDIO UPLOAD & VEO VIDEO GEN)
# -------------------------------------------------------------
if "config" in st.session_state:
    st.divider()
    st.subheader("🔍 Asset Verification & Generation")
    
    col_audio, col_video = st.columns([1, 2.5])
    
    # --- SECTION A: SUNO AUDIO UPLOAD ---
    with col_audio:
        st.markdown("### 🎵 1. Music Track (Suno AI)")
        audio_path = os.path.join(ASSETS_DIR, "music.mp3")
        
        uploaded_audio = st.file_uploader(
            "Upload Suno .mp3 audio", 
            type=["mp3"], 
            key="audio_drop"
        )
        
        if uploaded_audio is not None:
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())
            st.success("Saved as music.mp3!")
            st.rerun()
        
        if os.path.exists(audio_path):
            st.audio(audio_path)
            st.checkbox("Music Track Approved", key="audio_ok")
        else:
            st.info("Upload the .mp3 track downloaded from Suno AI.")

    # --- SECTION B: AUTOMATED VEO VIDEO GENERATION ---
    with col_video:
        st.markdown(f"### 🎬 2. Video Clips (Google Veo - {st.session_state['config']['aspect_ratio']})")
        scene_count = st.session_state["config"]["scene_count"]
        
        # Batch Render Button
        if st.button("🚀 Render All Scenes at Once", type="primary"):
            with st.spinner("Generating all video scenes via Google Veo (this may take a couple of minutes)..."):
                for i in range(scene_count):
                    scene_num = i + 1
                    scene_file = os.path.join(ASSETS_DIR, f"scene_{scene_num}.mp4")
                    prompt = st.session_state["prompts"][i]
                    try:
                        generate_scene_video(prompt, scene_file, st.session_state["config"]["aspect_ratio"])
                    except Exception as e:
                        st.error(f"Error rendering Scene {scene_num}: {e}")
                st.success("All scenes generated successfully!")
                st.rerun()

        st.write("") # Spacing
        
        # Individual Scene Columns
        v_cols = st.columns(scene_count)
        
        for i in range(scene_count):
            scene_num = i + 1
            scene_file = os.path.join(ASSETS_DIR, f"scene_{scene_num}.mp4")
            
            with v_cols[i]:
                st.caption(f"**Scene {scene_num}**")
                
                if os.path.exists(scene_file):
                    st.video(scene_file)
                    st.checkbox(f"Approve S{scene_num}", key=f"scene_ok_{scene_num}")
                    
                    if st.button(f"🔄 Regenerate S{scene_num}", key=f"regen_{scene_num}"):
                        with st.spinner(f"Regenerating Scene {scene_num}..."):
                            prompt = st.session_state["prompts"][i]
                            try:
                                generate_scene_video(prompt, scene_file, st.session_state["config"]["aspect_ratio"])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.info("Awaiting render...")
                    if st.button(f"🎬 Render S{scene_num}", key=f"gen_{scene_num}"):
                        with st.spinner(f"Rendering Scene {scene_num}..."):
                            prompt = st.session_state["prompts"][i]
                            try:
                                generate_scene_video(prompt, scene_file, st.session_state["config"]["aspect_ratio"])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

# -------------------------------------------------------------
# STEP 5: FINAL STITCHING (FFMPEG)
# -------------------------------------------------------------
st.divider()
if st.button("Assemble Final Video", type="primary"):
    count = st.session_state.get("config", {}).get("scene_count", 4)
    missing_scenes = [i+1 for i in range(count) if not os.path.exists(os.path.join(ASSETS_DIR, f"scene_{i+1}.mp4"))]
    audio_file = os.path.join(ASSETS_DIR, "music.mp3")

    if missing_scenes:
        st.error(f"Missing video files for scenes: {missing_scenes}. Please upload them first.")
    elif not os.path.exists(audio_file):
        st.error("Missing audio file ('music.mp3'). Please upload the track first.")
    else:
        with st.spinner("Stitching video scenes and merging audio with FFmpeg..."):
            try:
                final_path = assemble_video(ASSETS_DIR, count)
                st.success("Final video assembled successfully!")
                st.video(final_path)
            except Exception as e:
                st.error(f"Assembly Error: {e}")
