from core.base_exercise import BaseExercise


class PushUpDetector(BaseExercise):

    DOWN_THRESHOLD = 90
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

        hip_status = "GOOD"

        shoulder = self.get_point(landmarks, shoulder_idx)
        hip = self.get_point(landmarks, hip_idx)
        wrist = self.get_point(landmarks, wrist_idx)

        # Shoulder → hip → wrist alignment
        body_angle = self.calculate_angle(
            shoulder,
            hip,
            wrist
        )

        if body_angle < 160:
            hip_status = "HIPS TOO LOW"
        elif body_angle > 200:
            hip_status = "HIPS TOO HIGH"

        key_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[hip_idx].visibility >= self.MIN_VISIBILITY
        )

        if key_visible:

            if elbow_angle <= self.DOWN_THRESHOLD:
                self.stage = "down"

            if (
                elbow_angle >= self.UP_THRESHOLD
                and self.stage == "down"
            ):
                self.stage = "up"
                self.reps += 1

        if self.stage == "down":
            depth_status = (
                "GOOD DEPTH"
                if elbow_angle <= self.DOWN_THRESHOLD
                else "TOO HIGH"
            )

        elif self.stage == "up":
            depth_status = "UP"

        else:
            depth_status = "N/A"

        body_alignment = (
            "GOOD"
            if abs(body_angle - 180) <= 15
            else "CHECK ALIGNMENT"
        )

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "hip_status": hip_status,
            "body_alignment": body_alignment
        }