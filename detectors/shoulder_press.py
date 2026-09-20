from core.base_exercise import BaseExercise


class ShoulderPressDetector(BaseExercise):

    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15

    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16

    LEFT_HIP = 23
    RIGHT_HIP = 24

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

    def process(self, landmarks):

        left_elbow_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_SHOULDER),
            self.get_point(landmarks, self.LEFT_ELBOW),
            self.get_point(landmarks, self.LEFT_WRIST)
        )

        right_elbow_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_SHOULDER),
            self.get_point(landmarks, self.RIGHT_ELBOW),
            self.get_point(landmarks, self.RIGHT_WRIST)
        )

        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility

        if left_vis >= right_vis:

            elbow_angle = left_elbow_angle

            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP

        else:

            elbow_angle = right_elbow_angle

            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP

        key_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
        )

        if key_visible:

            # Bottom position
            if elbow_angle <= self.DOWN_THRESHOLD:
                self.stage = "down"

            # Full extension
            if (
                elbow_angle >= self.UP_THRESHOLD
                and self.stage == "down"
            ):
                self.stage = "up"
                self.reps += 1

        if self.stage == "up":
            extension_status = "FULL EXTENSION"

        elif self.stage == "down":
            extension_status = "PRESS"

        else:
            extension_status = "N/A"

        # Torso angle for back arch
        shoulder = self.get_point(landmarks, shoulder_idx)
        hip = self.get_point(landmarks, hip_idx)

        torso_angle = self.calculate_angle(
            self.get_point(landmarks, elbow_idx),
            shoulder,
            hip
        )

        back_arch_status = (
            "GOOD"
            if torso_angle >= 160
            else "EXCESSIVE ARCH"
        )

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "extension_status": extension_status,
            "back_arch_status": back_arch_status
        }