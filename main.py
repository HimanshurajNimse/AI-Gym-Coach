import streamlit as st
import time
from pathlib import Path
from dotenv import load_dotenv


from services.auth.login_wall import render_login_wall
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

        except Exception:
            st.session_state.voice_pipeline = None

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
                st.session_state["exercise_type"] = None

                if st.session_state.voice_pipeline:
                    result=st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={}
                    )

                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result
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
        st.audio(audio_data, format="audio/mp3")

    if st.session_state.get("coach_feedback"):
        st.success(f"**Coach:**{st.session_state.coach_feedback}")

    if not workout_started:

        st.html(
            """
            <div class="camera-section">
                <div class="camera-frame">
                    <div class="camera-placeholder">

                        <div class="camera-icon">
                            ◉
                        </div>

                        <div class="camera-placeholder-title">
                            CAMERA READY
                        </div>

                        <div class="camera-placeholder-text">
                            Choose your exercise and start your session
                            <br>
                            to begin real-time training.
                        </div>

                    </div>
                </div>
            </div>
            """
        )

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