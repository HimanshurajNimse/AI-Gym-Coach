import time
import streamlit as st

from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


def sync_metrics_update(context):
    """
    Synchronize live metrics from the WebRTC video processor
    into Streamlit session state.

    Also handles:
    - Rep and set calculations
    - Saving completed sets
    - Voice coaching events
    - Workout completion
    - No-pose detection
    """

    # Only process while the camera stream is active
    if (
        context is None
        or not hasattr(context, "state")
        or not context.state.playing
    ):
        return

    processor = getattr(context, "video_processor", None)

    if processor is None:
        return

    # Use the durable exercise state set when the workout starts
    exercise = (
        st.session_state.get("exercise_type")
        or st.session_state.get("plan_exercise")
    )

    if not exercise:
        return

    # Keep the processor synchronized with the selected exercise
    try:
        processor.set_exercise(exercise)
    except AttributeError:
        pass

    # Read the latest metrics from the processor
    try:
        latest_metrics = processor.get_latest_metrics()
    except AttributeError:
        return

    if not latest_metrics:
        return

    # ---------------------------------------------------------
    # 1. Synchronize repetitions
    # ---------------------------------------------------------

    reps = latest_metrics.get("reps", 0) or 0
    reps = max(0, int(reps))

    st.session_state["reps"] = reps

    # ---------------------------------------------------------
    # 2. Synchronize exercise-specific metrics
    # ---------------------------------------------------------

    fields = METRICS_FIELDS.get(exercise, {})

    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    # Also preserve general metrics returned by the processor
    for key, value in latest_metrics.items():
        if key != "reps":
            st.session_state[key] = value

    # ---------------------------------------------------------
    # 3. Calculate sets and workout progress
    # ---------------------------------------------------------

    reps_per_set = int(st.session_state.get("reps_per_set", 0) or 0)
    target_sets = int(st.session_state.get("target_sets", 0) or 0)

    if reps_per_set > 0 and target_sets > 0:
        sets_completed = min(reps // reps_per_set, target_sets)
        current_set_reps = reps % reps_per_set

        workout_completed = sets_completed >= target_sets
    else:
        sets_completed = 0
        current_set_reps = reps
        workout_completed = False

    st.session_state["sets_completed"] = sets_completed
    st.session_state["current_set_reps"] = current_set_reps
    st.session_state["workout_completed"] = workout_completed

    # ---------------------------------------------------------
    # 4. Save newly completed sets
    # ---------------------------------------------------------

    last_saved_sets = int(
        st.session_state.get("last_saved_sets_completed", 0) or 0
    )

    if (
        target_sets > 0
        and reps_per_set > 0
        and sets_completed > last_saved_sets
    ):
        newly_completed = sets_completed - last_saved_sets

        now_ts = time.time()
        started_at = st.session_state.get(
            "set_cycle_started_at",
            now_ts,
        )

        time_taken = max(0, now_ts - started_at)
        user_id = st.session_state.get("user_id", 0)

        add_exercise(
            user_id,
            exercise,
            newly_completed * reps_per_set,
            newly_completed,
            time_taken,
        )

        # Trigger set-completed coaching only once per newly completed set
        voice_pipeline = st.session_state.get("voice_pipeline")

        if voice_pipeline:
            result = voice_pipeline.process_event(
                event="set_completed",
                exercise=exercise,
                metrics=latest_metrics,
            )

            if result:
                (
                    st.session_state["audio_to_play"],
                    st.session_state["coach_feedback"],
                ) = result

        st.session_state["set_cycle_started_at"] = now_ts
        st.session_state["last_saved_sets_completed"] = sets_completed

    # ---------------------------------------------------------
    # 5. Workout completion event
    # ---------------------------------------------------------

    if (
        workout_completed
        and not st.session_state.get(
            "last_notified_workout_complete",
            False,
        )
    ):
        st.session_state["last_notified_workout_complete"] = True

        voice_pipeline = st.session_state.get("voice_pipeline")

        if voice_pipeline:
            result = voice_pipeline.process_event(
                event="workout_completed",
                exercise=exercise,
                metrics=latest_metrics,
            )

            if result:
                (
                    st.session_state["audio_to_play"],
                    st.session_state["coach_feedback"],
                ) = result

    # ---------------------------------------------------------
    # 6. No-pose-detected event
    # ---------------------------------------------------------

    pose_detected = latest_metrics.get("pose_detected", True)

    if not pose_detected:
        voice_pipeline = st.session_state.get("voice_pipeline")

        # Prevent triggering the same warning on every Streamlit rerun
        if not st.session_state.get("no_pose_warning_active", False):
            st.session_state["no_pose_warning_active"] = True

            if voice_pipeline:
                result = voice_pipeline.process_event(
                    event="no_pose_detected",
                    exercise=exercise,
                    metrics={
                        "issue": (
                            "No pose detected! "
                            "Please step into the camera frame."
                        )
                    },
                )

                if result:
                    (
                        st.session_state["audio_to_play"],
                        st.session_state["coach_feedback"],
                    ) = result
    else:
        st.session_state["no_pose_warning_active"] = False

    # ---------------------------------------------------------
    # 7. Ongoing form check
    # ---------------------------------------------------------

    voice_pipeline = st.session_state.get("voice_pipeline")

    if voice_pipeline and pose_detected:
        result = voice_pipeline.process_event(
            event="ongoing_form_check",
            exercise=exercise,
            metrics=latest_metrics,
        )

        if result:
            (
                st.session_state["audio_to_play"],
                st.session_state["coach_feedback"],
            ) = result