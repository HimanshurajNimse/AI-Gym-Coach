from core.base_exercise import BaseExercise


class StandingKneeRaiseDetector(BaseExercise):

    # =========================================================
    # THRESHOLDS
    # =========================================================

    DOWN_THRESHOLD = 25
    UP_THRESHOLD = 65

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
        self.stage = None

    # =========================================================
    # PROCESS
    # =========================================================

    def process(self, landmarks):

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
        # SELECT MORE VISIBLE SIDE
        # =====================================================

        left_vis = min(
            landmarks[self.LEFT_HIP].visibility,
            landmarks[self.LEFT_KNEE].visibility,
            landmarks[self.LEFT_SHOULDER].visibility
        )

        right_vis = min(
            landmarks[self.RIGHT_HIP].visibility,
            landmarks[self.RIGHT_KNEE].visibility,
            landmarks[self.RIGHT_SHOULDER].visibility
        )

        if left_vis >= right_vis:

            hip_angle = left_hip_angle

            shoulder_idx = self.LEFT_SHOULDER
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE

            visibility = left_vis

        else:

            hip_angle = right_hip_angle

            shoulder_idx = self.RIGHT_SHOULDER
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE

            visibility = right_vis

        # =====================================================
        # VISIBILITY CHECK
        # =====================================================

        key_landmark_visible = visibility >= self.MIN_VISIBILITY

        # =====================================================
        # REP DETECTION
        #
        # Leg down → UP → leg down = 1 rep
        # =====================================================

        if key_landmark_visible:

            if hip_angle <= self.DOWN_THRESHOLD:

                if self.stage == "up":
                    self.reps += 1

                self.stage = "down"

            elif hip_angle >= self.UP_THRESHOLD:

                self.stage = "up"

        # =====================================================
        # HIP STATUS
        # =====================================================

        if self.stage == "up":
            hip_status = "RAISED"

        elif self.stage == "down":
            hip_status = "DOWN"

        else:
            hip_status = "N/A"

        # =====================================================
        # TORSO ANGLE
        #
        # Shoulder → Hip → vertical reference through hip
        # =====================================================

        shoulder = self.get_point(
            landmarks,
            shoulder_idx
        )

        hip = self.get_point(
            landmarks,
            hip_idx
        )

        # A vertical reference point below the hip.
        vertical_point = (
            hip[0],
            hip[1] + 1.0
        )

        torso_angle = self.calculate_angle(
            shoulder,
            hip,
            vertical_point
        )

        # =====================================================
        # TORSO STATUS
        # =====================================================

        if torso_angle <= 15:

            torso_status = "UPRIGHT"

        elif torso_angle <= 30:

            torso_status = "SLIGHT LEAN"

        else:

            torso_status = "LEANING"

        # =====================================================
        # RETURN METRICS
        # =====================================================

        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "knee_angle": 0,
            "torso_status": torso_status,
        }