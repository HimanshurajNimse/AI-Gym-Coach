from core.base_exercise import BaseExercise


class BicepsCurlDetector(BaseExercise):

    DOWN_THRESHOLD = 150
    UP_THRESHOLD = 50
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15

    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

    def process(self, landmarks):

        left_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_SHOULDER),
            self.get_point(landmarks, self.LEFT_ELBOW),
            self.get_point(landmarks, self.LEFT_WRIST)
        )

        right_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_SHOULDER),
            self.get_point(landmarks, self.RIGHT_ELBOW),
            self.get_point(landmarks, self.RIGHT_WRIST)
        )

        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility

        if left_vis >= right_vis:

            elbow_angle = left_angle

            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST

        else:

            elbow_angle = right_angle

            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST

        key_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
        )

        if key_visible:

            # Arm extended
            if elbow_angle >= self.DOWN_THRESHOLD:
                self.stage = "down"

            # Arm curled
            if (
                elbow_angle <= self.UP_THRESHOLD
                and self.stage == "down"
            ):
                self.stage = "up"
                self.reps += 1

        if self.stage == "up":
            curl_status = "FULL CURL"

        elif self.stage == "down":
            curl_status = "EXTENDED"

        else:
            curl_status = "N/A"

        # Shoulder movement detection
        shoulder = self.get_point(landmarks, shoulder_idx)
        elbow = self.get_point(landmarks, elbow_idx)

        shoulder_angle = self.calculate_angle(
            self.get_point(landmarks, wrist_idx),
            shoulder,
            elbow
        )

        if shoulder_angle < 150:
            shoulder_status = "STABLE"
        else:
            shoulder_status = "CHECK SHOULDER"

        swing_status = (
            "CONTROLLED"
            if abs(shoulder_angle - 180) <= 30
            else "POSSIBLE SWING"
        )

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "shoulder_status": shoulder_status,
            "swing_status": swing_status
        }