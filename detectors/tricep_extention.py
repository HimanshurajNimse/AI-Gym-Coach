from core.base_exercise import BaseExercise


class TricepsExtensionDetector(BaseExercise):

    # =========================================================
    # THRESHOLDS
    # =========================================================

    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160

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
        # LEFT ELBOW ANGLE
        # Shoulder → Elbow → Wrist
        # =====================================================

        left_elbow_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.LEFT_SHOULDER
            ),
            self.get_point(
                landmarks,
                self.LEFT_ELBOW
            ),
            self.get_point(
                landmarks,
                self.LEFT_WRIST
            )
        )

        # =====================================================
        # RIGHT ELBOW ANGLE
        # =====================================================

        right_elbow_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.RIGHT_SHOULDER
            ),
            self.get_point(
                landmarks,
                self.RIGHT_ELBOW
            ),
            self.get_point(
                landmarks,
                self.RIGHT_WRIST
            )
        )

        # =====================================================
        # SELECT MORE VISIBLE ARM
        # =====================================================

        left_vis = min(
            landmarks[self.LEFT_SHOULDER].visibility,
            landmarks[self.LEFT_ELBOW].visibility,
            landmarks[self.LEFT_WRIST].visibility
        )

        right_vis = min(
            landmarks[self.RIGHT_SHOULDER].visibility,
            landmarks[self.RIGHT_ELBOW].visibility,
            landmarks[self.RIGHT_WRIST].visibility
        )

        if left_vis >= right_vis:

            elbow_angle = left_elbow_angle

            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST

            visibility = left_vis

        else:

            elbow_angle = right_elbow_angle

            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST

            visibility = right_vis

        # =====================================================
        # VISIBILITY CHECK
        # =====================================================

        key_landmark_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
        )

        # =====================================================
        # REP DETECTION
        #
        # Bent elbow  → DOWN
        # Extended arm → UP
        # =====================================================

        if key_landmark_visible:

            if elbow_angle <= self.DOWN_THRESHOLD:
                self.stage = "down"

            elif (
                elbow_angle >= self.UP_THRESHOLD
                and self.stage == "down"
            ):
                self.stage = "up"
                self.reps += 1

        # =====================================================
        # ARM EXTENSION STATUS
        # =====================================================

        if self.stage == "up":

            extension_status = "FULL EXTENSION"

        elif self.stage == "down":

            extension_status = "BENT"

        else:

            extension_status = "N/A"

        # =====================================================
        # SHOULDER STABILITY
        #
        # Compare shoulder/elbow relationship to detect
        # excessive elbow movement.
        # =====================================================

        shoulder = self.get_point(
            landmarks,
            shoulder_idx
        )

        elbow = self.get_point(
            landmarks,
            elbow_idx
        )

        # Horizontal shoulder-elbow displacement
        horizontal_offset = abs(
            shoulder[0] - elbow[0]
        )

        if horizontal_offset < 0.18:
            shoulder_status = "STABLE"
        else:
            shoulder_status = "MOVE LESS"

        # =====================================================
        # RETURN METRICS
        # =====================================================

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "upper_arm_status": extension_status,
            "shoulder_status": shoulder_status,
        }