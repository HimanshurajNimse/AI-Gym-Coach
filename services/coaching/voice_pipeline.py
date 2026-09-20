import time
import streamlit as st




class VoicePipeline:

    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0
        self.last_issue = None

    def _find_form_issue(self, exercise, metrics):

        if not isinstance(metrics, dict):
            return None

        if metrics.get("issue"):
            return metrics["issue"]

        if exercise == "Squats":

            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)

            if depth == "TOO HIGH":
                return (
                    "The user's squat is not deep enough. "
                    "Ask them to bend their knees more."
                )

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return (
                    "The user is leaning too far forward during the squat. "
                    "Ask them to keep their chest more upright."
                )

        elif exercise == "Push-ups":

            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")

            if alignment == "Poor Form":
                return "The user's body is not straight during the push-up."

            if hip_status == "SAGGING":
                return (
                    "The user's hips are sagging. "
                    "Ask them to keep their body straight."
                )

            if hip_status == "PIKED UP":
                return (
                    "The user's hips are too high. "
                    "Ask them to maintain a straight body line."
                )

        elif exercise == "Biceps Curls (Dumbbell)":

            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")

            if swing == "SWINGING":
                return (
                    "The user is swinging their torso. "
                    "Ask them to keep their body still."
                )

            if shoulder == "ELBOW DRIFTING":
                return "The user's elbows are drifting away from their sides."

        elif exercise == "Shoulder Press":

            back_arch = metrics.get("back_arch_status", "")
            extension = metrics.get("extension_status", "")

            if back_arch == "Excessive Arch":
                return (
                    "The user is arching their lower back excessively. "
                    "Ask them to brace their core."
                )

            if back_arch == "Slight Arch":
                return (
                    "A slight back arch was detected. "
                    "Ask the user to brace their core."
                )

            if extension == "INSUFFICIENT":
                return (
                    "The user is not fully extending their arms "
                    "during the shoulder press."
                )

        elif exercise == "Lunges":

            balance = metrics.get("balance_status", "")

            if balance == "OFF BALANCE":
                return (
                    "The user is losing balance during the lunge. "
                    "Ask them to keep their feet hip-width apart."
                )

        elif exercise == "Glute Bridges":

            hip_extension = metrics.get("hip_extension_status", "")

            if hip_extension in {"INSUFFICIENT", "LOW"}:
                return (
                    "The user's hips are not extending high enough. "
                    "Ask them to squeeze their glutes at the top."
                )

        elif exercise == "Calf Raises":

            heel_status = metrics.get("heel_status", "")
            knee_status = metrics.get("knee_status", "")

            if heel_status in {"INSUFFICIENT", "LOW"}:
                return (
                    "The user is not raising their heels high enough. "
                    "Ask them to rise onto their toes."
                )

            if knee_status in {"BENT", "UNSTABLE"}:
                return (
                    "The user's knees are not stable during the calf raise. "
                    "Ask them to keep their legs controlled."
                )

        elif exercise == "Triceps Extensions":

            upper_arm_status = metrics.get("upper_arm_status", "")
            shoulder_status = metrics.get("shoulder_status", "")

            if upper_arm_status in {"MOVING", "UNSTABLE"}:
                return (
                    "The user's upper arms are moving too much. "
                    "Ask them to keep their elbows steady."
                )

            if shoulder_status in {"MOVING", "UNSTABLE"}:
                return (
                    "The user's shoulders are moving during the extension. "
                    "Ask them to keep their shoulders stable."
                )

        elif exercise == "Lateral Raises":

            shoulder_status = metrics.get("shoulder_status", "")

            if shoulder_status in {"TOO HIGH", "SHRUGGING"}:
                return (
                    "The user is raising their shoulders too high. "
                    "Ask them to avoid shrugging."
                )

            if shoulder_status in {"UNCONTROLLED", "POOR FORM"}:
                return (
                    "The lateral raise is uncontrolled. "
                    "Ask the user to move slowly."
                )

        elif exercise == "Front Raises":

            shoulder_status = metrics.get("shoulder_status", "")

            if shoulder_status in {"TOO HIGH", "SHRUGGING"}:
                return (
                    "The user is raising the weights too high. "
                    "Ask them to keep the movement controlled."
                )

            if shoulder_status in {"UNCONTROLLED", "POOR FORM"}:
                return (
                    "The front raise is uncontrolled. "
                    "Ask the user to move slowly without swinging."
                )

        elif exercise == "Standing Knee Raises":

            torso_status = metrics.get("torso_status", "")

            if torso_status in {"LEANING", "UNSTABLE", "POOR FORM"}:
                return (
                    "The user's torso is unstable during the knee raise. "
                    "Ask them to keep their upper body upright."
                )

        elif exercise == "Mountain Climbers":

            alignment = metrics.get("body_alignment", "")

            if alignment in {"Poor Form", "UNSTABLE"}:
                return (
                    "The user's body alignment is poor during mountain climbers. "
                    "Ask them to keep their body in a straight plank position."
                )

        return None

    def process_event(self, event, exercise, metrics):

        issue = self._find_form_issue(exercise, metrics)
        now = time.time()

        major_events = {
            "workout_started",
            "set_completed",
            "workout_completed",
        }

        if event not in major_events:

            if not issue:
                return None

            if issue == self.last_issue and now - self.last_spoken_at < 5:
                return None

            if now - self.last_spoken_at < 10:
                return None

        if issue:
            if "session_issues" not in st.session_state:
                st.session_state["session_issues"] = []
            if issue != self.last_issue:
                st.session_state["session_issues"].append(issue)

        try:
            text = self.llm.give_feedback(event, exercise=exercise, issue=issue)
        except Exception as e:
            print(f"LLM error: {e}")
            return None, f"LLM error: {e}"

        if not text:
            return None

        try:
            voice = self.tts.speak(text)
        except Exception as e:
            print(f"TTS error: {e}")
            return None, f"TTS error: {e}"

        if not voice:
            return None, "TTS error: returned empty audio"

        self.last_spoken_at = time.time()
        self.last_issue = issue

        return voice, text


def autoplay_audio(audio_bytes):
    if audio_bytes:
        st.audio(
            audio_bytes,
            format="audio/mp3",
            autoplay=True
        )