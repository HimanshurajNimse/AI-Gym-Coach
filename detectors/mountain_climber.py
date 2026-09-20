from core.base_exercise import BaseExercise


class MountainClimberDetector(BaseExercise):

    # =========================================================
    # THRESHOLDS
    # =========================================================

    # Knee must move sufficiently toward the chest.
    KNEE_RAISE_THRESHOLD = 85

    # Knee must return sufficiently straight before
    # the same leg can count again.
    KNEE_EXTENDED_THRESHOLD = 150

    # Maximum acceptable hip deviation from plank position.
    HIP_ALIGNMENT_THRESHOLD = 25

    MIN_VISIBILITY = 0.7

    # =========================================================
    # MEDIAPIPE LANDMARKS
    # =========================================================

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):
        super().__init__()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):
        self.reps = 0

        self.left_stage = "extended"
        self.right_stage = "extended"

        self.stage = None

    # =========================================================
    # PROCESS
    # =========================================================

    def process(self, landmarks):

        # =====================================================
        # LEFT KNEE ANGLE
        #
        # Hip → Knee → Ankle
        # =====================================================

        left_knee_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.LEFT_HIP
            ),
            self.get_point(
                landmarks,
                self.LEFT_KNEE
            ),
            self.get_point(
                landmarks,
                self.LEFT_ANKLE
            )
        )

        # =====================================================
        # RIGHT KNEE ANGLE
        # =====================================================

        right_knee_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.RIGHT_HIP
            ),
            self.get_point(
                landmarks,
                self.RIGHT_KNEE
            ),
            self.get_point(
                landmarks,
                self.RIGHT_ANKLE
            )
        )

        # =====================================================
        # LEFT HIP ANGLE
        #
        # Shoulder → Hip → Knee
        # =====================================================

        left_hip_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.LEFT_SHOULDER
            ),
            self.get_point(
                landmarks,
                self.LEFT_HIP
            ),
            self.get_point(
                landmarks,
                self.LEFT_KNEE
            )
        )

        # =====================================================
        # RIGHT HIP ANGLE
        # =====================================================

        right_hip_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.RIGHT_SHOULDER
            ),
            self.get_point(
                landmarks,
                self.RIGHT_HIP
            ),
            self.get_point(
                landmarks,
                self.RIGHT_KNEE
            )
        )

        # =====================================================
        # VISIBILITY
        # =====================================================

        left_vis = min(
            landmarks[self.LEFT_SHOULDER].visibility,
            landmarks[self.LEFT_HIP].visibility,
            landmarks[self.LEFT_KNEE].visibility,
            landmarks[self.LEFT_ANKLE].visibility
        )

        right_vis = min(
            landmarks[self.RIGHT_SHOULDER].visibility,
            landmarks[self.RIGHT_HIP].visibility,
            landmarks[self.RIGHT_KNEE].visibility,
            landmarks[self.RIGHT_ANKLE].visibility
        )

        key_landmarks_visible = (
            left_vis >= self.MIN_VISIBILITY
            and right_vis >= self.MIN_VISIBILITY
        )

        if not key_landmarks_visible:

            return {
                "reps": self.reps,
                "knee_angle": 0,
                "hip_angle": 0,
                "body_alignment": "NO POSE",
            }

        # =====================================================
        # LEFT LEG
        # =====================================================

        if left_knee_angle <= self.KNEE_RAISE_THRESHOLD:

            if self.left_stage == "extended":

                self.left_stage = "raised"

                self.reps += 1

                self.stage = "left"

        elif left_knee_angle >= self.KNEE_EXTENDED_THRESHOLD:

            self.left_stage = "extended"

        # =====================================================
        # RIGHT LEG
        # =====================================================

        if right_knee_angle <= self.KNEE_RAISE_THRESHOLD:

            if self.right_stage == "extended":

                self.right_stage = "raised"

                self.reps += 1

                self.stage = "right"

        elif right_knee_angle >= self.KNEE_EXTENDED_THRESHOLD:

            self.right_stage = "extended"

        # =====================================================
        # CURRENT KNEE
        # =====================================================

        if self.stage == "left":

            knee_angle = left_knee_angle
            hip_angle = left_hip_angle

        elif self.stage == "right":

            knee_angle = right_knee_angle
            hip_angle = right_hip_angle

        else:

            knee_angle = min(
                left_knee_angle,
                right_knee_angle
            )

            hip_angle = min(
                left_hip_angle,
                right_hip_angle
            )

        # =====================================================
        # BODY ALIGNMENT
        #
        # In a good mountain climber position, the hips should
        # remain relatively controlled instead of excessively
        # rising or dropping.
        # =====================================================

        left_alignment = abs(
            180 - left_hip_angle
        )

        right_alignment = abs(
            180 - right_hip_angle
        )

        alignment_error = max(
            left_alignment,
            right_alignment
        )

        if alignment_error <= self.HIP_ALIGNMENT_THRESHOLD:

            body_alignment = "GOOD"

        elif alignment_error <= 40:

            body_alignment = "SLIGHT MISALIGNMENT"

        else:

            body_alignment = "POOR ALIGNMENT"

        # =====================================================
        # RETURN METRICS
        # =====================================================

        return {
            "reps": self.reps,
            "knee_angle": int(knee_angle),
            "hip_angle": int(hip_angle),
            "body_alignment": body_alignment,
        }