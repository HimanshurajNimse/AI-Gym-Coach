import streamlit as st


def initial_session_defaults():

    defaults = {

        # =====================================================
        # WORKOUT STATE
        # =====================================================

        "reps": 0,
        "target_sets": 0,
        "reps_per_set": 0,
        "sets_completed": 0,
        "current_set_reps": 0,

        "workout_complete": False,
        "workout_started": False,

        "last_notified_sets_completed": 0,
        "last_notified_workout_complete": False,
        "last_saved_sets_completed": 0,

        "set_cycle_started_at": 0.0,

        "last_exercise_type": "Squats",


        # =====================================================
        # ACTIVE WORKOUT PLAN
        # =====================================================

        # These are the values actually used by the workout.
        "plan_exercise": "Squats",
        "plan_sets": 3,
        "plan_reps": 10,


        # =====================================================
        # WORKOUT PLAN WIDGET STATE
        # =====================================================

        # IMPORTANT:
        # These are separate from plan_exercise / plan_sets /
        # plan_reps because the widgets disappear after the
        # workout starts.

        "plan_exercise_selector": "Squats",
        "plan_sets_selector": 3,
        "plan_reps_selector": 10,


        # =====================================================
        # COMMON ANGLES
        # =====================================================

        "knee_angle": 0,
        "back_angle": 0,
        "elbow_angle": 0,

        "front_knee_angle": 0,
        "torso_angle": 0,

        "hip_angle": 0,
        "arm_angle": 0,
        "ankle_angle": 0,


        # =====================================================
        # COMMON STATUS FIELDS
        # =====================================================

        "depth_status": "N/A",
        "body_alignment": "N/A",
        "hip_status": "N/A",

        "shoulder_status": "N/A",
        "swing_status": "N/A",

        "extension_status": "N/A",
        "back_arch_status": "N/A",

        "balance_status": "N/A",


        # =====================================================
        # GLUTE BRIDGES
        # =====================================================

        "hip_extension_status": "N/A",


        # =====================================================
        # CALF RAISES
        # =====================================================

        "knee_status": "N/A",
        "heel_status": "N/A",


        # =====================================================
        # TRICEPS EXTENSIONS
        # =====================================================

        "upper_arm_status": "N/A",


        # =====================================================
        # STANDING KNEE RAISES
        # =====================================================

        "torso_status": "N/A",
    }


    # =========================================================
    # INITIALIZE ONLY IF NOT ALREADY PRESENT
    # =========================================================

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value