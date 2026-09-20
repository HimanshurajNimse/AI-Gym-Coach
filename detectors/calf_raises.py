from core.base_exercise import BaseExercise


class CalfRaiseDetector(BaseExercise):

    # =========================================================
    # THRESHOLDS
    # =========================================================

    # Minimum normalized heel movement required to consider
    # the heel raised. Tune these values with real footage.
    RAISE_THRESHOLD = 0.035
    LOWER_THRESHOLD = 0.015

    MIN_VISIBILITY = 0.7

    # =========================================================
    # MEDIAPIPE LANDMARKS
    # =========================================================

    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    LEFT_HEEL = 29
    RIGHT_HEEL = 30

    LEFT_FOOT = 31
    RIGHT_FOOT = 32

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

        self.baseline_left_heel = None
        self.baseline_right_heel = None

    # =========================================================
    # PROCESS
    # =========================================================

    def process(self, landmarks):

        # -----------------------------------------------------
        # Landmark visibility
        # -----------------------------------------------------

        left_vis = min(
            landmarks[self.LEFT_ANKLE].visibility,
            landmarks[self.LEFT_HEEL].visibility,
            landmarks[self.LEFT_FOOT].visibility
        )

        right_vis = min(
            landmarks[self.RIGHT_ANKLE].visibility,
            landmarks[self.RIGHT_HEEL].visibility,
            landmarks[self.RIGHT_FOOT].visibility
        )

        # -----------------------------------------------------
        # Select the more visible side
        # -----------------------------------------------------

        if left_vis >= right_vis:

            ankle_idx = self.LEFT_ANKLE
            heel_idx = self.LEFT_HEEL
            foot_idx = self.LEFT_FOOT
            knee_idx = self.LEFT_KNEE

            visibility = left_vis

        else:

            ankle_idx = self.RIGHT_ANKLE
            heel_idx = self.RIGHT_HEEL
            foot_idx = self.RIGHT_FOOT
            knee_idx = self.RIGHT_KNEE

            visibility = right_vis

        # -----------------------------------------------------
        # Check required landmarks
        # -----------------------------------------------------

        if visibility < self.MIN_VISIBILITY:

            return {
                "reps": self.reps,
                "ankle_angle": 0,
                "knee_status": "N/A",
                "heel_status": "NO POSE",
            }

        # -----------------------------------------------------
        # Get landmarks
        # -----------------------------------------------------

        heel = self.get_point(
            landmarks,
            heel_idx
        )

        ankle = self.get_point(
            landmarks,
            ankle_idx
        )

        foot = self.get_point(
            landmarks,
            foot_idx
        )

        knee = self.get_point(
            landmarks,
            knee_idx
        )

        # -----------------------------------------------------
        # Establish baseline
        #
        # MediaPipe Y increases downward.
        # Therefore a smaller heel Y means the heel moved UP.
        # -----------------------------------------------------

        if self.baseline_left_heel is None:

            self.baseline_left_heel = landmarks[
                self.LEFT_HEEL
            ].y

        if self.baseline_right_heel is None:

            self.baseline_right_heel = landmarks[
                self.RIGHT_HEEL
            ].y

        if heel_idx == self.LEFT_HEEL:
            baseline_heel_y = self.baseline_left_heel
        else:
            baseline_heel_y = self.baseline_right_heel

        # -----------------------------------------------------
        # Calculate normalized heel displacement
        #
        # Use knee → ankle distance as body-scale reference.
        # This makes the threshold less dependent on distance
        # from the camera.
        # -----------------------------------------------------

        body_scale = abs(
            knee[1] - ankle[1]
        )

        if body_scale < 1e-6:
            body_scale = 1.0

        heel_rise = (
            baseline_heel_y - heel[1]
        ) / body_scale

        # -----------------------------------------------------
        # Heel movement
        # -----------------------------------------------------

        if heel_rise >= self.RAISE_THRESHOLD:

            current_stage = "up"

        elif heel_rise <= self.LOWER_THRESHOLD:

            current_stage = "down"

        else:

            current_stage = self.stage

        # -----------------------------------------------------
        # REP DETECTION
        # -----------------------------------------------------

        if current_stage == "up":

            if self.stage == "down":

                self.reps += 1

            self.stage = "up"

        elif current_stage == "down":

            self.stage = "down"

        # -----------------------------------------------------
        # HEEL STATUS
        # -----------------------------------------------------

        if self.stage == "up":

            heel_status = "RAISED"

        elif self.stage == "down":

            heel_status = "GROUND"

        else:

            heel_status = "N/A"

        # -----------------------------------------------------
        # KNEE STABILITY
        # -----------------------------------------------------

        knee_angle = self.calculate_angle(
            self.get_point(
                landmarks,
                self.LEFT_HIP if knee_idx == self.LEFT_KNEE
                else self.RIGHT_HIP
            ),
            knee,
            ankle
        )

        if 155 <= knee_angle <= 180:

            knee_status = "STABLE"

        else:

            knee_status = "BENDING"

        # -----------------------------------------------------
        # RETURN METRICS
        # -----------------------------------------------------

        return {
            "reps": self.reps,
            "ankle_angle": int(heel_rise * 100),
            "knee_status": knee_status,
            "heel_status": heel_status,
        }