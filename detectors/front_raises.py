from core.base_exercise import BaseExercise


class FrontRaiseDetector(BaseExercise):

    # =========================================================
    # THRESHOLDS
    # =========================================================

    DOWN_THRESHOLD = 25
    UP_THRESHOLD = 70

    MIN_VISIBILITY = 0.7

    # =========================================================
    # MEDIAPIPE LANDMARKS
    # =========================================================

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14

    LEFT_WRIST = 15
    RIGHT_WRIST = 16

    LEFT_HIP = 23
    RIGHT_HIP = 24

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
        # LEFT ARM ELEVATION
        #
        # Hip → Shoulder → Elbow
        # =====================================================

        left_arm_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_SHOULDER),
            self.get_point(landmarks, self.LEFT_ELBOW)
        )

        # =====================================================
        # RIGHT ARM ELEVATION
        # =====================================================

        right_arm_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_SHOULDER),
            self.get_point(landmarks, self.RIGHT_ELBOW)
        )

        # =====================================================
        # LEFT ELBOW ANGLE
        #
        # Shoulder → Elbow → Wrist
        # =====================================================

        left_elbow_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_SHOULDER),
            self.get_point(landmarks, self.LEFT_ELBOW),
            self.get_point(landmarks, self.LEFT_WRIST)
        )

        # =====================================================
        # RIGHT ELBOW ANGLE
        # =====================================================

        right_elbow_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_SHOULDER),
            self.get_point(landmarks, self.RIGHT_ELBOW),
            self.get_point(landmarks, self.RIGHT_WRIST)
        )

        # =====================================================
        # VISIBILITY
        # =====================================================

        left_vis = min(
            landmarks[self.LEFT_SHOULDER].visibility,
            landmarks[self.LEFT_ELBOW].visibility,
            landmarks[self.LEFT_WRIST].visibility,
            landmarks[self.LEFT_HIP].visibility
        )

        right_vis = min(
            landmarks[self.RIGHT_SHOULDER].visibility,
            landmarks[self.RIGHT_ELBOW].visibility,
            landmarks[self.RIGHT_WRIST].visibility,
            landmarks[self.RIGHT_HIP].visibility
        )

        # =====================================================
        # SELECT MORE VISIBLE SIDE
        # =====================================================

        if left_vis >= right_vis:

            arm_angle = left_arm_angle
            elbow_angle = left_elbow_angle

            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST

            visibility = left_vis

        else:

            arm_angle = right_arm_angle
            elbow_angle = right_elbow_angle

            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST

            visibility = right_vis

        # =====================================================
        # VISIBILITY CHECK
        # =====================================================

        key_landmark_visible = visibility >= self.MIN_VISIBILITY

        # =====================================================
        # REP DETECTION
        #
        # DOWN → UP → DOWN = 1 REP
        # =====================================================

        if key_landmark_visible:

            if arm_angle <= self.DOWN_THRESHOLD:
                if self.stage == "up":
                    self.reps += 1

                self.stage = "down"

            elif arm_angle >= self.UP_THRESHOLD:
                self.stage = "up"

        # =====================================================
        # SHOULDER STATUS
        # =====================================================

        if self.stage == "up":
            shoulder_status = "RAISED"

        elif self.stage == "down":
            shoulder_status = "DOWN"

        else:
            shoulder_status = "N/A"

        # =====================================================
        # ELBOW STATUS
        # =====================================================

        if elbow_angle >= 150:
            elbow_status = "GOOD"

        else:
            elbow_status = "BENT"

        # =====================================================
        # RETURN METRICS
        # =====================================================

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "arm_angle": int(arm_angle),
            "shoulder_status": shoulder_status,
        }