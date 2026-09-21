import streamlit as st
import time
from pathlib import Path
from dotenv import load_dotenv


from services.auth.login_wall import render_login_wall
from ui.muscle_map import render_muscle_map
from services.state.session_default import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.persistence.exercise_repository import init_db
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.matrics import sync_metrics_update

from services.coaching.llm import *
from services.coaching.voice_pipeline import *
from services.coaching.tts import *

from streamlit_webrtc import webrtc_streamer, WebRtcMode
import streamlit.components.v1 as components

# =========================================================
# API INITIALIZATION
# =========================================================
load_dotenv()  # Load environment variables from .env file
import os
# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_icon="💪🏻",
    page_title="AI real-time GYM Coach",
    initial_sidebar_state="expanded",
    layout="centered",
)


# =========================================================
# GLOBAL CSS
# =========================================================

css_path = Path("static/style.css")

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


# =========================================================
# BROWSER RESIZE
# =========================================================

def trigger_browser_resize():
    components.html(
        """
        <script>
            setTimeout(() => {
                window.parent.dispatchEvent(new Event("resize"));
            }, 300);
        </script>
        """,
        height=0,
    )

# =========================================================
#WORKOUT HISTORY
# =========================================================

import pandas as pd

from services.persistence.exercise_repository import get_users_exercises


def render_workout_history():

    user_id = st.session_state.get("user_id", 0)

    if not isinstance(user_id, int):
        st.info("No valid user found.")
        return

    history_rows = get_users_exercises(user_id)

    arr = [
        {
            "Exercise": row["exercise_name"],
            "Reps": row["reps"],
            "Sets": row["sets"],
            "Time (sec)": row["time"],
            "Date": row["created_at"],
        }
        for row in history_rows
    ]

    df = pd.DataFrame(
        arr,
        columns=[
            "Exercise",
            "Reps",
            "Sets",
            "Time (sec)",
            "Date",
        ],
    )

    if df.empty:
        st.info("No workout history found.")
        return

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

    agg_df = (
        df.groupby(["Exercise", "Date"], as_index=False)
        .agg({
            "Reps": "sum",
            "Sets": "sum",
            "Time (sec)": "sum",
        })
    )

    agg_df.index += 1

    st.table(agg_df)


# =========================================================
# LIVE METRIC HELPERS
# =========================================================

def metric_value(key, default="N/A"):
    value = st.session_state.get(key, default)

    if value is None:
        return default

    return value


def angle_value(key):
    value = st.session_state.get(key, 0)

    if value is None:
        return "—"

    try:
        return f"{float(value):.1f}°"
    except (TypeError, ValueError):
        return str(value)


def render_live_metrics(exercise):
    """
    Render live values already synchronized by sync_metrics_update().
    This function does not modify workout logic or session calculations.
    """

    st.html(
        """
        <div class="sidebar-section-label">
            LIVE PROGRESS
        </div>
        """
    )

    total_reps = st.session_state.get("reps", 0)
    current_set_reps = st.session_state.get("current_set_reps", 0)
    reps_per_set = st.session_state.get("reps_per_set", 0)
    sets_completed = st.session_state.get("sets_completed", 0)
    target_sets = st.session_state.get("target_sets", 0)

    st.html(
        f"""
        <div class="progress-grid">

            <div class="progress-card">
                <div class="progress-label">
                    TOTAL REPS
                </div>
                <div class="progress-value">
                    {total_reps}
                </div>
            </div>

            <div class="progress-card">
                <div class="progress-label">
                    SETS
                </div>
                <div class="progress-value">
                    {sets_completed}
                    <span>/{target_sets}</span>
                </div>
            </div>

            <div class="progress-card wide">
                <div class="progress-label">
                    CURRENT REPS
                </div>
                <div class="progress-value">
                    {current_set_reps}
                    <span>/{reps_per_set}</span>
                </div>
            </div>

        </div>
        """
    )

    st.html(
        """
        <div class="sidebar-section-label">
            FORM ANALYSIS
        </div>
        """
    )

    if exercise == "Squats":

        st.html(
            '<div class="metric-heading">SQUAT ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Knee Angle",
                angle_value("knee_angle"),
            )

        with col2:
            st.metric(
                "Back Angle",
                angle_value("back_angle"),
            )

        st.metric(
            "Depth Status",
            metric_value("depth_status"),
        )

    elif exercise == "Push-ups":

        st.html(
            '<div class="metric-heading">PUSH-UP ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Elbow Angle",
                angle_value("elbow_angle"),
            )

        with col2:
            st.metric(
                "Hip Position",
                metric_value("hip_status"),
            )

        st.metric(
            "Body Alignment",
            metric_value("body_alignment"),
        )

    elif exercise == "Biceps Curls (Dumbbell)":

        st.html(
            '<div class="metric-heading">CURL ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Elbow Angle",
                angle_value("elbow_angle"),
            )

        with col2:
            st.metric(
                "Shoulder",
                metric_value("shoulder_status"),
            )

        st.metric(
            "Swing Detection",
            metric_value("swing_status"),
        )

    elif exercise == "Shoulder Press":

        st.html(
            '<div class="metric-heading">PRESS ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Elbow Angle",
                angle_value("elbow_angle"),
            )

        with col2:
            st.metric(
                "Extension",
                metric_value("extension_status"),
            )

        st.metric(
            "Back Arch",
            metric_value("back_arch_status"),
        )

    elif exercise == "Lunges":

        st.html(
            '<div class="metric-heading">LUNGE ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Front Knee",
                angle_value("front_knee_angle"),
            )

        with col2:
            st.metric(
                "Torso Angle",
                angle_value("torso_angle"),
            )

        st.metric(
            "Balance",
            metric_value("balance_status"),
        )

    elif exercise == "Glute Bridges":

        st.html(
            '<div class="metric-heading">GLUTE BRIDGE ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Hip Angle",
                angle_value("hip_angle"),
            )

        with col2:
            st.metric(
                "Knee Angle",
                angle_value("knee_angle"),
            )

        st.metric(
            "Hip Extension",
            metric_value("hip_extension_status"),
        )

    elif exercise == "Calf Raises":

        st.html(
            '<div class="metric-heading">CALF RAISE ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Ankle Angle",
                angle_value("ankle_angle"),
            )

        with col2:
            st.metric(
                "Knee Position",
                metric_value("knee_status"),
            )

        st.metric(
            "Heel Position",
            metric_value("heel_status"),
        )

    elif exercise == "Triceps Extensions":

        st.html(
            '<div class="metric-heading">TRICEPS ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Elbow Angle",
                angle_value("elbow_angle"),
            )

        with col2:
            st.metric(
                "Upper Arm",
                metric_value("upper_arm_status"),
            )

        st.metric(
            "Shoulder Stability",
            metric_value("shoulder_status"),
        )

    elif exercise == "Lateral Raises":

        st.html(
            '<div class="metric-heading">LATERAL RAISE ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Elbow Angle",
                angle_value("elbow_angle"),
            )

        with col2:
            st.metric(
                "Arm Angle",
                angle_value("arm_angle"),
            )

        st.metric(
            "Shoulder Position",
            metric_value("shoulder_status"),
        )

    elif exercise == "Front Raises":

        st.html(
            '<div class="metric-heading">FRONT RAISE ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Elbow Angle",
                angle_value("elbow_angle"),
            )

        with col2:
            st.metric(
                "Arm Angle",
                angle_value("arm_angle"),
            )

        st.metric(
            "Shoulder Position",
            metric_value("shoulder_status"),
        )

    elif exercise == "Standing Knee Raises":

        st.html(
            '<div class="metric-heading">KNEE RAISE ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Hip Angle",
                angle_value("hip_angle"),
            )

        with col2:
            st.metric(
                "Knee Angle",
                angle_value("knee_angle"),
            )

        st.metric(
            "Torso Position",
            metric_value("torso_status"),
        )

    elif exercise == "Mountain Climbers":

        st.html(
            '<div class="metric-heading">MOUNTAIN CLIMBER ANALYSIS</div>'
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Knee Angle",
                angle_value("knee_angle"),
            )

        with col2:
            st.metric(
                "Hip Angle",
                angle_value("hip_angle"),
            )

        st.metric(
            "Body Alignment",
            metric_value("body_alignment"),
        )


# =========================================================
# MAIN
# =========================================================

def main():

    init_db()



    if not render_login_wall():
        return

    initial_session_defaults()
    st.session_state.setdefault("audio_to_play", None)
    st.session_state.setdefault("coach_feedback", "")

    if "voice_pipeline" not in st.session_state:

        try:
            llm_coach = LLMCoach()
            tts = TextToSpeech()

            st.session_state.voice_pipeline = VoicePipeline(
                llm=llm_coach,
                tts=tts
            )
            
            # Welcome message when pipeline is initialized (user logged in)
            username = st.session_state.get("username", "")
            welcome_text = f"Welcome {username}, let's get ready for your workout!"
            try:
                st.session_state["audio_to_play"] = tts.speak(welcome_text)
                st.session_state["coach_feedback"] = welcome_text
            except Exception as e:
                print(f"TTS Welcome Error: {e}")

        except Exception as e:
            st.session_state.voice_pipeline = None
            st.error(f"Failed to initialize voice pipeline: {e}")

    workout_started = st.session_state.get(
        "workout_started",
        False
    )

    


    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        # =================================================
        # PROFILE
        # =================================================

        st.html(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-mark">AI</div>
                <div>
                    <div class="sidebar-brand-title">GYM COACH</div>
                    <div class="sidebar-brand-subtitle">
                        REAL-TIME TRAINING
                    </div>
                </div>
            </div>
            """
        )

        if st.session_state.get("username"):

            st.html(
                f"""
                <div class="user-card">
                    <div class="user-status">
                        <span class="status-dot"></span>
                        SESSION ACTIVE
                    </div>
                    <div class="user-name">
                        {st.session_state.username}
                    </div>
                </div>
                """
            )

        st.html(
            """
            <div class="sidebar-section-label">
                WORKOUT PLAN
            </div>
            """
        )

        # =================================================
        # WORKOUT PLAN — BEFORE SESSION
        # =================================================

        if not workout_started:

            st.selectbox(
                "Exercise",
                options=EXERCISE_OPTIONS,
                key="plan_exercise_selector",
            )

            col1, col2 = st.columns(2)

            with col1:
                st.number_input(
                    "Sets",
                    min_value=0,
                    max_value=50,
                    key="plan_sets_selector",
                    step=1,
                )

            with col2:
                st.number_input(
                    "Reps",
                    min_value=0,
                    max_value=100,
                    key="plan_reps_selector",
                    step=1,
                )

            st.html('<div style="height:8px"></div>')

            start_session_button = st.button(
                "START SESSION  →",
                width="stretch",
                key="start_session_button",
            )

            if start_session_button:

                plan_exercise=st.session_state["plan_exercise"] = (
                    st.session_state["plan_exercise_selector"]
                )

                st.session_state["plan_sets"] = (
                    st.session_state["plan_sets_selector"]
                )

                st.session_state["plan_reps"] = (
                    st.session_state["plan_reps_selector"]
                )

                st.session_state["exercise_type"] = (
                    st.session_state["plan_exercise"]
                )

                st.session_state["target_sets"] = (
                    st.session_state["plan_sets"]
                )

                st.session_state["reps_per_set"] = (
                    st.session_state["plan_reps"]
                )

                st.session_state["reps"] = 0
                st.session_state["current_set_reps"] = 0
                st.session_state["sets_completed"] = 0
                st.session_state["workout_complete"] = False
                st.session_state["workout_completed"] = False

                st.session_state["last_saved_sets_completed"] = 0
                st.session_state["last_notified_workout_complete"] = False
                st.session_state["no_pose_warning_active"] = False
                st.session_state["set_cycle_started_at"] = time.time()

                st.session_state["workout_started"] = True

                voice_pipeline = st.session_state.get("voice_pipeline")

                if voice_pipeline is not None:
                    try:
                        result = voice_pipeline.process_event(
                            event="workout_started",
                            exercise=plan_exercise,
                            metrics={}
                        )

                        if result and isinstance(result, tuple):
                            audio_data, feedback = result

                            st.session_state["audio_to_play"] = audio_data
                            st.session_state["coach_feedback"] = feedback or ""

                    except Exception as e:
                        st.session_state["coach_feedback"] = (
                            f"Voice coach error: {str(e)}"
                        )

                st.session_state["knee_angle"] = 0
                st.session_state["back_angle"] = 0
                st.session_state["depth_status"] = "N/A"

                st.session_state["elbow_angle"] = 0
                st.session_state["shoulder_status"] = "N/A"
                st.session_state["swing_status"] = "N/A"

                st.session_state["extension_status"] = "N/A"
                st.session_state["back_arch_status"] = "N/A"

                st.session_state["front_knee_angle"] = 0
                st.session_state["torso_angle"] = 0
                st.session_state["balance_status"] = "N/A"

                st.session_state["hip_angle"] = 0
                st.session_state["hip_extension_status"] = "N/A"

                st.session_state["ankle_angle"] = 0
                st.session_state["knee_status"] = "N/A"
                st.session_state["heel_status"] = "N/A"

                st.session_state["upper_arm_status"] = "N/A"
                st.session_state["arm_angle"] = 0
                st.session_state["torso_status"] = "N/A"
                st.session_state["body_alignment"] = "N/A"
                st.session_state["hip_status"] = "N/A"

                st.session_state["workout_started"] = True

                st.rerun()

        # =================================================
        # ACTIVE WORKOUT
        # =================================================

        else:

            exercise = st.session_state.get(
                "plan_exercise",
                "Squats",
            )

            st.session_state["exercise_type"] = exercise

            sets = st.session_state.get("plan_sets", 0)
            reps = st.session_state.get("plan_reps", 0)

            st.html(
                f"""
                <div class="active-workout-card">
                    <div class="active-label">
                        CURRENT WORKOUT
                    </div>

                    <div class="active-exercise">
                        {exercise}
                    </div>

                    <div class="active-details">
                        <span>{sets} SETS</span>
                        <span class="detail-divider">•</span>
                        <span>{reps} REPS</span>
                    </div>
                </div>
                """
            )

            end_session_button = st.button(
                "END SESSION",
                key="end_session_button",
                width="stretch",
            )

            if end_session_button:
                st.session_state["workout_started"] = False
                
                # Fetch actual completed reps and sets
                actual_reps = st.session_state.get("reps", 0)
                actual_sets = st.session_state.get("sets_completed", 0)
                
                # Fetch AI Post-Workout Summary only if they did work
                if (actual_reps > 0 or actual_sets > 0) and st.session_state.voice_pipeline and hasattr(st.session_state.voice_pipeline.llm, "generate_workout_summary"):
                    issues = st.session_state.get("session_issues", [])
                    try:
                        summary = st.session_state.voice_pipeline.llm.generate_workout_summary(
                            exercise=exercise,
                            reps=actual_reps,
                            sets=actual_sets,
                            form_issues=issues
                        )
                        st.session_state["post_workout_summary"] = summary
                        
                        # Make coach say the summary
                        try:
                            st.session_state["audio_to_play"] = st.session_state.voice_pipeline.tts.speak(summary)
                            st.session_state["coach_feedback"] = summary
                        except:
                            pass
                    except Exception as e:
                        print(f"Summary Error: {e}")
                elif actual_reps == 0 and actual_sets == 0:
                    aborted_msg = "Session aborted. No reps recorded. Take a breather and let's get back to it when you're ready!"
                    st.session_state["post_workout_summary"] = aborted_msg
                    if st.session_state.voice_pipeline:
                        try:
                            st.session_state["audio_to_play"] = st.session_state.voice_pipeline.tts.speak(aborted_msg)
                            st.session_state["coach_feedback"] = aborted_msg
                        except:
                            pass
                
                st.session_state["show_summary"] = True
                
                # Clear session issues
                if "session_issues" in st.session_state:
                    del st.session_state["session_issues"]
                
                st.rerun()

            render_live_metrics(exercise)

    # =====================================================
    # MAIN SCREEN
    # =====================================================

    st.markdown("### LIVE TRAINING")
    st.markdown(
        "Real-time camera feed for movement and form analysis.",
    )

    audio_data = st.session_state.get("audio_to_play")

    if audio_data:
        import base64
        b64 = base64.b64encode(audio_data).decode()
        st.html(f'<audio autoplay style="display:none;" src="data:audio/mp3;base64,{b64}"></audio>')

    if st.session_state.get("coach_feedback") and not st.session_state.get("show_summary"):
        st.success(f"**Coach:** {st.session_state.coach_feedback}")

    if st.session_state.get("show_summary"):
        sets_done = st.session_state.get("sets_completed", 0)
        reps_done = st.session_state.get("reps", 0)
        
        if sets_done == 0 and reps_done == 0:
            st.markdown("### SESSION ABORTED ⚠️")
            st.warning("You ended the session before completing any reps. No progress was recorded. Stay focused and try again next time!")
            if st.button("DISMISS", use_container_width=True):
                st.session_state["show_summary"] = False
                st.session_state["coach_feedback"] = ""
                st.session_state["audio_to_play"] = None
                st.rerun()
        else:
            # Check if they hit the target
            target_sets = st.session_state.get("plan_sets", 0)
            if sets_done >= target_sets:
                st.markdown("### WORKOUT COMPLETE 🏆")
            else:
                st.markdown("### WORKOUT INCOMPLETE ⏱️")

            # Badges
            issues = st.session_state.get("session_issues", [])
            badges = []
            if len(issues) == 0:
                badges.append("🏆 Perfect Form")
            else:
                badges.append("🛡️ Iron Will")
            if reps_done >= 15:
                badges.append("🔥 Volume Warrior")
                
            badge_html = " ".join([f"<span style='background: #333; padding: 5px 12px; border-radius: 15px; margin-right: 10px; font-weight: bold; color: #f36c21; font-size: 0.9rem;'>{b}</span>" for b in badges])
            
            st.html(f"""
            <div style="margin-bottom: 20px;">
                {badge_html}
            </div>
            <div style="background-color: #1a1a1a; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #333;">
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div><h4 style="color: #888; margin:0;">Sets Completed</h4><h2 style="margin:0; color: #fff;">{sets_done}</h2></div>
                    <div><h4 style="color: #888; margin:0;">Total Reps</h4><h2 style="margin:0; color: #fff;">{reps_done}</h2></div>
                </div>
            </div>
            """)
            
            # Form Report section
            if len(issues) > 0:
                st.markdown("### 📋 Form Report")
                for issue in issues:
                    st.warning(f"⚠️ {issue}")
            else:
                st.markdown("### 📋 Form Report")
                st.success("✅ Flawless execution! No form mistakes detected.")
                
            summary = st.session_state.get("post_workout_summary", "Great job! Keep up the good work.")
            st.info(f"**Coach's Notes:** {summary}")
            
            render_muscle_map(st.session_state.get("exercise_type", "Squats"))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("DISCARD", use_container_width=True):
                    st.session_state["show_summary"] = False
                    st.session_state["coach_feedback"] = ""
                    st.session_state["audio_to_play"] = None
                    st.rerun()
            with col2:
                if st.button("SAVE WORKOUT", use_container_width=True, type="primary"):
                    # Save partial/full workout to history if needed
                    from services.persistence.exercise_repository import add_exercise
                    user_id = st.session_state.get("user_id", 0)
                    add_exercise(
                        user_id=user_id,
                        exercise_name=st.session_state.get("exercise_type", "Squats"),
                        reps=reps_done,
                        sets=sets_done,
                        time=0 # Time calculation can be added if tracked
                    )
                    st.session_state["show_summary"] = False
                    st.session_state["coach_feedback"] = ""
                    st.session_state["audio_to_play"] = None
                    st.rerun()

    elif not workout_started:

        st.html(
            """
            <div class="camera-section">
                <div class="camera-frame">
                    <div class="camera-placeholder">
                        <div class="camera-icon">◉</div>
                        <div class="camera-placeholder-title">CAMERA READY</div>
                        <div class="camera-placeholder-text">
                            Choose your exercise and start your session<br>to begin real-time training.
                        </div>
                    </div>
                </div>
            </div>
            """
        )
        
        # Use the selector state so it updates instantly before they click start
        exercise = st.session_state.get("plan_exercise_selector", "Squats")
        
        # Generic placeholder tutorials (open-source / YouTube fitness channels)
        tutorial_vids = {
            "Squats": "https://www.youtube.com/watch?v=gcNh17Ckjgg",
            "Push-ups": "https://www.youtube.com/watch?v=IODxDxX7oi4",
            "Biceps Curls (Dumbbell)": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
            "Shoulder Press": "https://www.youtube.com/watch?v=qEwKCR5JCog",
            "Lunges": "https://www.youtube.com/watch?v=QOVaHwm-Q6U",
            "Glute Bridges": "https://www.youtube.com/watch?v=wPM8icPu6H8",
            "Calf Raises": "https://www.youtube.com/watch?v=-M4-G8p8fmc",
            "Triceps Extensions": "https://www.youtube.com/watch?v=nRiJVZDpdL0",
            "Lateral Raises": "https://www.youtube.com/watch?v=3VcKaXpzqRo",
            "Front Raises": "https://www.youtube.com/watch?v=-t7fuZ0KhDA",
            "Standing Knee Raises": "https://www.youtube.com/watch?v=0hAZo84sL7o",
            "Mountain Climbers": "https://www.youtube.com/watch?v=nmwgirgXLYM"
        }
        
        if exercise in tutorial_vids:
            
            @st.dialog(f"Tutorial: {exercise}")
            def show_tutorial_dialog(video_url):
                st.video(video_url)
                
            if st.button(f"📺 View Tutorial: {exercise}"):
                show_tutorial_dialog(tutorial_vids[exercise])

    else:

        exercise = st.session_state.get(
            "plan_exercise",
            "Squats",
        )

        st.session_state["exercise_type"] = exercise

        st.html(
            f"""
            <div class="training-status">
                <span class="status-dot"></span>
                <span>LIVE TRAINING</span>
                <span class="status-exercise">
                    {exercise}
                </span>
            </div>
            """
        )

        trigger_browser_resize()

        # =================================================
        # WEBRTC
        # =================================================

        context = webrtc_streamer(
            key=f"exercise-analysis-{exercise}",
            mode=WebRtcMode.SENDRECV,

            media_stream_constraints={
                "video": {
                    "width": {"ideal": 1280},
                    "height": {"ideal": 720},
                    "facingMode": "user",
                },
                "audio": False,
            },

            video_html_attrs={
                "autoPlay": True,
                "controls": False,
                "muted": True,
                "playsInline": True,
                "style": {
                    "width": "100%",
                    "height": "auto",
                    "display": "block",
                    "border-radius": "16px",
                },
            },

            video_processor_factory=lambda: VideoProcessorClass(
                exercise_type=exercise,
            ),

            rtc_configuration={
                "iceServers": [
                    {
                        "urls": [
                            "stun:stun.l.google.com:19302"
                        ]
                    }
                ]
            },

            async_processing=True,
        )

        # Synchronize metrics and preserve the existing logic.
        sync_metrics_update(context)

        # Refresh only while the camera is active.
        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

    # =====================================================
    # WORKOUT HISTORY
    # =====================================================

    st.html(
        """
        <div class="history-header">
            <h3>WORKOUT HISTORY</h3>
            <p>
                Your previous training sessions and performance.
            </p>
        </div>
        """
    )
    render_workout_history()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()