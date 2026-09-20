from core.base_exercise import BaseExercise


class GluteBridgeDetector(BaseExercise):

    DOWN_THRESHOLD = 150
    UP_THRESHOLD = 170
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

    def process(self, landmarks):

        # =====================================================
        # LEFT SIDE
        # =====================================================

        left_hip_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_SHOULDER),
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE)
        )

        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE)
        )

        # =====================================================
        # RIGHT SIDE
        # =====================================================

        right_hip_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_SHOULDER),
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE)
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE)
        )

        # =====================================================
        # SELECT MORE VISIBLE SIDE
        # =====================================================

        left_vis = landmarks[self.LEFT_HIP].visibility
        right_vis = landmarks[self.RIGHT_HIP].visibility

        if left_vis >= right_vis:

            hip_angle = left_hip_angle
            knee_angle = left_knee_angle

            shoulder_idx = self.LEFT_SHOULDER
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
            ankle_idx = self.LEFT_ANKLE

        else:

            hip_angle = right_hip_angle
            knee_angle = right_knee_angle

            shoulder_idx = self.RIGHT_SHOULDER
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE
            ankle_idx = self.RIGHT_ANKLE

        # =====================================================
        # VISIBILITY
        # =====================================================

        key_landmark_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[hip_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[knee_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[ankle_idx].visibility >= self.MIN_VISIBILITY
        )

        # =====================================================
        # REP DETECTION
        # =====================================================

        if key_landmark_visible:

            # Lower position
            if hip_angle < self.DOWN_THRESHOLD:
                self.stage = "down"

            # Full hip extension
            elif (
                hip_angle >= self.UP_THRESHOLD
                and self.stage == "down"
            ):
                self.stage = "up"
                self.reps += 1

        # =====================================================
        # STATUS
        # =====================================================

        if self.stage == "up":
            hip_extension_status = "FULL EXTENSION"

        elif self.stage == "down":
            hip_extension_status = "LOWERED"

        else:
            hip_extension_status = "N/A"

        # =====================================================
        # RETURN
        # =====================================================

        return {
            "reps": self.reps,
            "hip_angle": int(hip_angle),
            "knee_angle": int(knee_angle),
            "hip_extension_status": hip_extension_status,
        }