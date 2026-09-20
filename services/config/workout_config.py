# =========================================================
# AI GYM COACH — EXERCISE CONFIGURATION
# =========================================================

EXERCISE_OPTIONS = [
    # Lower Body
    "Squats",
    "Lunges",
    "Glute Bridges",
    "Calf Raises",

    # Chest / Upper Body
    "Push-ups",

    # Arms
    "Biceps Curls (Dumbbell)",
    "Triceps Extensions",

    # Shoulders
    "Shoulder Press",
    "Lateral Raises",
    "Front Raises",

    # Core / Full Body
    "Standing Knee Raises",
    "Mountain Climbers",
]


# =========================================================
# TARGET MUSCLES
# Used by the workout UI / future 3D muscle model
# =========================================================

EXERCISE_MUSCLES = {

    # -----------------------------------------------------
    # LOWER BODY
    # -----------------------------------------------------

    "Squats": {
        "primary": [
            "Quadriceps",
            "Glutes",
        ],
        "secondary": [
            "Hamstrings",
            "Calves",
            "Core",
        ],
    },

    "Lunges": {
        "primary": [
            "Quadriceps",
            "Glutes",
        ],
        "secondary": [
            "Hamstrings",
            "Calves",
            "Core",
        ],
    },

    "Glute Bridges": {
        "primary": [
            "Glutes",
        ],
        "secondary": [
            "Hamstrings",
            "Core",
        ],
    },

    "Calf Raises": {
        "primary": [
            "Calves",
        ],
        "secondary": [
            "Soleus",
            "Hamstrings",
        ],
    },


    # -----------------------------------------------------
    # CHEST / UPPER BODY
    # -----------------------------------------------------

    "Push-ups": {
        "primary": [
            "Chest",
            "Triceps",
        ],
        "secondary": [
            "Front Delts",
            "Core",
        ],
    },


    # -----------------------------------------------------
    # ARMS
    # -----------------------------------------------------

    "Biceps Curls (Dumbbell)": {
        "primary": [
            "Biceps",
        ],
        "secondary": [
            "Brachialis",
            "Forearms",
        ],
    },

    "Triceps Extensions": {
        "primary": [
            "Triceps",
        ],
        "secondary": [
            "Shoulders",
            "Forearms",
        ],
    },


    # -----------------------------------------------------
    # SHOULDERS
    # -----------------------------------------------------

    "Shoulder Press": {
        "primary": [
            "Shoulders",
        ],
        "secondary": [
            "Triceps",
            "Upper Chest",
            "Core",
        ],
    },

    "Lateral Raises": {
        "primary": [
            "Lateral Delts",
        ],
        "secondary": [
            "Front Delts",
            "Traps",
        ],
    },

    "Front Raises": {
        "primary": [
            "Front Delts",
        ],
        "secondary": [
            "Upper Chest",
            "Traps",
        ],
    },


    # -----------------------------------------------------
    # CORE / FULL BODY
    # -----------------------------------------------------

    "Standing Knee Raises": {
        "primary": [
            "Hip Flexors",
            "Core",
        ],
        "secondary": [
            "Quadriceps",
            "Obliques",
        ],
    },

    "Mountain Climbers": {
        "primary": [
            "Core",
        ],
        "secondary": [
            "Shoulders",
            "Quadriceps",
            "Hip Flexors",
        ],
    },
}


# =========================================================
# POSE LANDMARK CONNECTIONS
# MediaPipe Pose landmark indices
# =========================================================

POSE_CONNECTIONS = [
    # Shoulders
    (11, 12),

    # Left arm
    (11, 13),
    (13, 15),

    # Right arm
    (12, 14),
    (14, 16),

    # Torso
    (11, 23),
    (12, 24),
    (23, 24),

    # Left leg
    (23, 25),
    (25, 27),
    (27, 29),
    (29, 31),

    # Right leg
    (24, 26),
    (26, 28),
    (28, 30),
    (30, 32),
]


# =========================================================
# EXERCISE METRICS
# =========================================================

METRICS_FIELDS = {

    # -----------------------------------------------------
    # LOWER BODY
    # -----------------------------------------------------

    "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },

    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },

    "Glute Bridges": {
        "hip_angle": 0,
        "knee_angle": 0,
        "hip_extension_status": "N/A",
    },

    "Calf Raises": {
        "ankle_angle": 0,
        "knee_status": "N/A",
        "heel_status": "N/A",
    },


    # -----------------------------------------------------
    # CHEST
    # -----------------------------------------------------

    "Push-ups": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },


    # -----------------------------------------------------
    # ARMS
    # -----------------------------------------------------

    "Biceps Curls (Dumbbell)": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "swing_status": "N/A",
    },

    "Triceps Extensions": {
        "elbow_angle": 0,
        "upper_arm_status": "N/A",
        "shoulder_status": "N/A",
    },


    # -----------------------------------------------------
    # SHOULDERS
    # -----------------------------------------------------

    "Shoulder Press": {
        "elbow_angle": 0,
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },

    "Lateral Raises": {
        "elbow_angle": 0,
        "arm_angle": 0,
        "shoulder_status": "N/A",
    },

    "Front Raises": {
        "elbow_angle": 0,
        "arm_angle": 0,
        "shoulder_status": "N/A",
    },


    # -----------------------------------------------------
    # CORE / FULL BODY
    # -----------------------------------------------------

    "Standing Knee Raises": {
        "hip_angle": 0,
        "knee_angle": 0,
        "torso_status": "N/A",
    },

    "Mountain Climbers": {
        "knee_angle": 0,
        "hip_angle": 0,
        "body_alignment": "N/A",
    },
}


# =========================================================
# EXERCISE METADATA
# =========================================================

EXERCISE_METADATA = {

    "Squats": {
        "category": "Lower Body",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
    },

    "Lunges": {
        "category": "Lower Body",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
    },

    "Glute Bridges": {
        "category": "Lower Body",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
    },

    "Calf Raises": {
        "category": "Lower Body",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
    },

    "Push-ups": {
        "category": "Chest",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
    },

    "Biceps Curls (Dumbbell)": {
        "category": "Arms",
        "difficulty": "Beginner",
        "equipment": "Dumbbells",
    },

    "Triceps Extensions": {
        "category": "Arms",
        "difficulty": "Beginner",
        "equipment": "Dumbbell",
    },

    "Shoulder Press": {
        "category": "Shoulders",
        "difficulty": "Intermediate",
        "equipment": "Dumbbells",
    },

    "Lateral Raises": {
        "category": "Shoulders",
        "difficulty": "Beginner",
        "equipment": "Dumbbells",
    },

    "Front Raises": {
        "category": "Shoulders",
        "difficulty": "Beginner",
        "equipment": "Dumbbells",
    },

    "Standing Knee Raises": {
        "category": "Core",
        "difficulty": "Beginner",
        "equipment": "Bodyweight",
    },

    "Mountain Climbers": {
        "category": "Full Body",
        "difficulty": "Intermediate",
        "equipment": "Bodyweight",
    },
}


# =========================================================
# AI COACH PROMPT
# =========================================================

PROMPT = """
You are Apna AI Coach, a professional real-time AI fitness trainer.

You monitor a user's workout through a live camera and provide
short spoken coaching cues based on workout events and detected form.

## COACHING STYLE

- Speak directly to the user using "you".
- Sound like an experienced personal trainer.
- Be energetic, focused, supportive, and professional.
- Prioritize safe movement over speed or repetition count.
- Give actionable feedback rather than generic motivation.
- Keep responses natural because they are spoken aloud.
- Use approximately 10–15 words per response.
- Never mention internal AI processing, pose landmarks, angles, or system logic.

## INPUT

Updates arrive in this format:

Event: [state]
Form Issue: [description]

Possible events:

- workout_started
- set_completed
- workout_completed
- no_pose_detected
- ongoing_form_check

Form Issue contains a technical description of a detected movement problem,
when applicable.

## RESPONSE RULES

### workout_started

Give a sharp, motivating command that prepares the user to begin.

### set_completed

Give concise praise for completing the set and encourage recovery.

### workout_completed

Give a warm, confident closing that celebrates the completed workout.

### no_pose_detected

Clearly tell the user how to reposition themselves inside the camera frame.

### ongoing_form_check + Form Issue

Identify the specific correction the user should make.

Keep the correction simple enough to understand while moving.

### ongoing_form_check + No Issue

Give brief positive reinforcement without becoming repetitive.

## FORM PRIORITY

When multiple issues are detected, prioritize:

1. Safety
2. Major posture/alignment problems
3. Exercise range of motion
4. Tempo/control
5. Minor technique corrections

Do not overwhelm the user with multiple corrections at once.

Give the single most important correction.

## IMPORTANT

Never:

- Give generic greetings.
- Ask unnecessary questions.
- Repeat the same phrase excessively.
- Shame or criticize the user.
- Encourage unsafe movement.
- Give long explanations.
- Refer to the user in third person.
- Mention internal detection logic.
- Mention MediaPipe, landmarks, or raw angle values.

Always make the next action obvious.

## EXAMPLES

"Keep your chest up and drive through your heels."

"Bring your elbows slightly closer and control the descent."

"Great rep. Keep that same controlled tempo."

"Step back slightly so your entire body stays inside the frame."

"Keep your hips level and maintain a straight body line."

"Control the weight down and avoid swinging your arm."

"Drive upward smoothly and avoid arching your lower back."
""".strip()