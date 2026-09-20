import os
import cv2
import av
import numpy as np
import mediapipe as mp
import threading
import time

from streamlit_webrtc import VideoProcessorBase

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# =========================================================
# EXERCISE DETECTORS
# =========================================================

from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungeDetector

from detectors.glute_bridge import GluteBridgeDetector
from detectors.calf_raises import CalfRaiseDetector
from detectors.tricep_extention import TricepsExtensionDetector
from detectors.lateral_raises import LateralRaiseDetector
from detectors.front_raises import FrontRaiseDetector
from detectors.knee_raises import StandingKneeRaiseDetector
from detectors.mountain_climber import MountainClimberDetector

from services.config.workout_config import POSE_CONNECTIONS


class VideoProcessorClass(VideoProcessorBase):

    def __init__(self, exercise_type="Squats"):

        # =====================================================
        # THREAD SAFETY
        # =====================================================

        self._lock = threading.Lock()

        self._latest_metrics = {
            "pose_detected": False
        }

        self._exercise_type = exercise_type

        # =====================================================
        # MEDIAPIPE POSE LANDMARKER
        # =====================================================

        model_path = os.path.join(
            os.getcwd(),
            "ml_models",
            "pose_landmarker_full.task"
        )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Pose model not found: {model_path}"
            )

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            output_segmentation_masks=False
        )

        self._landmarker = (
            vision.PoseLandmarker.create_from_options(options)
        )

        # =====================================================
        # DETECTORS
        # =====================================================

        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungeDetector(),
            "Glute Bridges": GluteBridgeDetector(),
            "Calf Raises": CalfRaiseDetector(),
            "Triceps Extensions": TricepsExtensionDetector(),
            "Lateral Raises": LateralRaiseDetector(),
            "Front Raises": FrontRaiseDetector(),
            "Standing Knee Raises": StandingKneeRaiseDetector(),
            "Mountain Climbers": MountainClimberDetector(),
        }

        if self._exercise_type not in self._detectors:
            self._exercise_type = "Squats"

        # =====================================================
        # TIMESTAMP
        # =====================================================

        self._last_timestamp_ms = 0

    # =========================================================
    # METRICS
    # =========================================================

    def set_latest_metrics(self, metrics):

        with self._lock:
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):

        with self._lock:

            if self._latest_metrics is None:
                return None

            return self._latest_metrics.copy()

    # =========================================================
    # EXERCISE
    # =========================================================

    def set_exercise(self, exercise_type):

        with self._lock:

            # Avoid resetting the detector on every Streamlit rerun
            if exercise_type == self._exercise_type:
                return

            self._exercise_type = exercise_type

            detector = self._detectors.get(exercise_type)

            if detector is not None:
                detector.reset()

            self._latest_metrics = {
                "pose_detected": False,
                "reps": 0
            }

    def get_exercise(self):

        with self._lock:
            return self._exercise_type

    # =========================================================
    # SKELETON
    # =========================================================

    def _draw_skeleton(self, img, landmarks):

        h, w = img.shape[:2]

        # -----------------------------------------------------
        # BONES
        # -----------------------------------------------------

        for start_idx, end_idx in POSE_CONNECTIONS:

            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]

            if (
                p1.visibility >= 0.7
                and p2.visibility >= 0.7
            ):

                cv2.line(
                    img,
                    (
                        int(p1.x * w),
                        int(p1.y * h)
                    ),
                    (
                        int(p2.x * w),
                        int(p2.y * h)
                    ),
                    (0, 255, 0),
                    4
                )

        # -----------------------------------------------------
        # JOINTS
        # -----------------------------------------------------

        for landmark in landmarks:

            if landmark.visibility >= 0.7:

                cv2.circle(
                    img,
                    (
                        int(landmark.x * w),
                        int(landmark.y * h)
                    ),
                    6,
                    (255, 0, 0),
                    -1
                )

    # =========================================================
    # NO POSE WARNING
    # =========================================================

    def _draw_no_pose_warnings(self, img):

        cv2.putText(
            img,
            "NO POSE DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    # =========================================================
    # GENERIC METRIC OVERLAY
    # =========================================================

    def _draw_metric(self, img, text):

        h, _ = img.shape[:2]

        cv2.putText(
            img,
            text,
            (20, h - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    # =========================================================
    # EXERCISE OVERLAYS
    # =========================================================

    def _draw_overlays(self, img, metrics, exercise):

        if exercise == "Squats":

            self._draw_metric(
                img,
                f"DEPTH: {metrics.get('depth_status', 'N/A')}"
            )

        elif exercise == "Push-ups":

            self._draw_metric(
                img,
                "BODY: "
                f"{metrics.get('body_alignment', 'N/A')} | "
                "HIP: "
                f"{metrics.get('hip_status', 'N/A')}"
            )

        elif exercise == "Biceps Curls (Dumbbell)":

            self._draw_metric(
                img,
                "SWING: "
                f"{metrics.get('swing_status', 'N/A')}"
            )

        elif exercise == "Shoulder Press":

            self._draw_metric(
                img,
                "EXT: "
                f"{metrics.get('extension_status', 'N/A')} | "
                "BACK: "
                f"{metrics.get('back_arch_status', 'N/A')}"
            )

        elif exercise == "Lunges":

            self._draw_metric(
                img,
                f"BALANCE: "
                f"{metrics.get('balance_status', 'N/A')}"
            )

        elif exercise == "Glute Bridges":

            self._draw_metric(
                img,
                f"HIP: "
                f"{metrics.get('hip_extension_status', 'N/A')}"
            )

        elif exercise == "Calf Raises":

            self._draw_metric(
                img,
                "HEEL: "
                f"{metrics.get('heel_status', 'N/A')} | "
                "KNEE: "
                f"{metrics.get('knee_status', 'N/A')}"
            )

        elif exercise == "Triceps Extensions":

            self._draw_metric(
                img,
                "ARM: "
                f"{metrics.get('upper_arm_status', 'N/A')} | "
                "SHOULDER: "
                f"{metrics.get('shoulder_status', 'N/A')}"
            )

        elif exercise == "Lateral Raises":

            self._draw_metric(
                img,
                f"SHOULDER: "
                f"{metrics.get('shoulder_status', 'N/A')}"
            )

        elif exercise == "Front Raises":

            self._draw_metric(
                img,
                f"SHOULDER: "
                f"{metrics.get('shoulder_status', 'N/A')}"
            )

        elif exercise == "Standing Knee Raises":

            self._draw_metric(
                img,
                f"TORSO: "
                f"{metrics.get('torso_status', 'N/A')}"
            )

        elif exercise == "Mountain Climbers":

            self._draw_metric(
                img,
                f"ALIGNMENT: "
                f"{metrics.get('body_alignment', 'N/A')}"
            )

    # =========================================================
    # FRAME PROCESSING
    # =========================================================

    def recv(self, frame):

        # -----------------------------------------------------
        # GET FRAME
        # -----------------------------------------------------

        image = frame.to_ndarray(format="bgr24")

        # Mirror webcam like a normal selfie camera
        image = cv2.flip(image, 1)

        # -----------------------------------------------------
        # MEDIAPIPE EXPECTS RGB
        # -----------------------------------------------------

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_image
        )

        # -----------------------------------------------------
        # MONOTONIC TIMESTAMP
        # -----------------------------------------------------

        timestamp_ms = int(time.monotonic() * 1000)

        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1

        self._last_timestamp_ms = timestamp_ms

        # -----------------------------------------------------
        # POSE DETECTION
        # -----------------------------------------------------

        result = self._landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        # -----------------------------------------------------
        # NO POSE
        # -----------------------------------------------------

        if not result.pose_landmarks:

            self._draw_no_pose_warnings(image)

            with self._lock:
                self._latest_metrics = {
                    "pose_detected": False
                }

            return av.VideoFrame.from_ndarray(
                image,
                format="bgr24"
            )

        # -----------------------------------------------------
        # LANDMARKS
        # -----------------------------------------------------

        landmarks = result.pose_landmarks[0]

        self._draw_skeleton(
            image,
            landmarks
        )

        # -----------------------------------------------------
        # CURRENT EXERCISE
        # -----------------------------------------------------

        exercise = self.get_exercise()

        detector = self._detectors.get(exercise)

        # -----------------------------------------------------
        # DETECTOR
        # -----------------------------------------------------

        if detector is not None:

            try:

                metrics = detector.process(landmarks)

                if metrics is None:
                    metrics = {}

                metrics["pose_detected"] = True

                # -------------------------------------------------
                # DRAW FEEDBACK ON CAMERA
                # -------------------------------------------------

                self._draw_overlays(
                    image,
                    metrics,
                    exercise
                )

                # -------------------------------------------------
                # SAVE LATEST METRICS
                # -------------------------------------------------

                self.set_latest_metrics(metrics)

            except Exception as error:

                # Keep the error in the metrics instead of printing
                self.set_latest_metrics({
                    "pose_detected": True,
                    "reps": 0,
                    "error": True,
                    "error_message": str(error)
                })

        # -----------------------------------------------------
        # RETURN FRAME
        # -----------------------------------------------------

        return av.VideoFrame.from_ndarray(
            image,
            format="bgr24"
        )