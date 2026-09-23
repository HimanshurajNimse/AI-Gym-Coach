# 🦾 AI Gym Coach

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54.0-FF4B4B.svg)
![Groq](https://img.shields.io/badge/Groq-Llama%203.1-orange.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-00A67E.svg)

The **AI Gym Coach** is a real-time, zero-latency computer vision training protocol. It uses your webcam to track your biomechanics in 3D space, and utilizes **Groq's Llama 3.1** and **TTS (Text-to-Speech)** to give you instant, personalized voice coaching while you work out.

---

## ✨ Features

- **🔴 Real-Time Pose Tracking**: Leverages Google's MediaPipe for blazing-fast 33-point skeletal tracking right in your browser via WebRTC.
- **🗣️ Live Voice Coaching**: Uses Groq's insanely fast inference engine (Llama 3.1) to analyze your form in real-time and provide spoken, constructive feedback (e.g. "Keep your chest up", "Explode on the way up").
- **🗺️ 2D Muscle Heatmaps**: After each session, view a glowing anatomical heatmap that shows exactly which muscle groups were activated based on your specific biomechanics.
- **📊 Local Workout History**: Every set, rep, and session duration is securely logged to a local SQLite database (`data.db`) so you can track your volume over time.
- **🌐 Next.js Landing Page**: Includes a sleek, glassmorphic React front-end designed to showcase the engine's capabilities.

## 🛠️ Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/) & [Streamlit-WebRTC](https://github.com/whitphx/streamlit-webrtc)
- **Computer Vision**: [OpenCV](https://opencv.org/) & [MediaPipe Pose](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker)
- **AI / LLM Engine**: [Groq API](https://groq.com/) (Llama 3.1 8B Instant)
- **Voice Engine**: gTTS (Google Text-to-Speech)
- **Database**: SQLite3
- **Landing Page**: Next.js 15, React, Tailwind CSS, Framer Motion

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/HimanshurajNimse/AI-Gym-Coach.git
cd AI-Gym-Coach
```

### 2. Set up the Environment
Ensure you have Python installed, then create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirement.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```

### 5. Launch the Coach
```bash
streamlit run main.py
```
Open `http://localhost:8501` in your browser. Ensure your browser allows camera access!

---

## ☁️ Deploying to the Cloud

This app is 100% ready to be deployed for free on **Streamlit Community Cloud**. 

Unlike many WebRTC apps that require paid TURN servers (like Twilio) to work over the internet, this codebase comes pre-configured with a **free Google STUN server** (`stun.l.google.com:19302`). This ensures the live camera feed will successfully connect for the vast majority of users on standard home and mobile networks without needing any paid infrastructure!

**To Deploy:**
1. Connect your GitHub to [share.streamlit.io](https://share.streamlit.io/).
2. Select this repository and set the main file to `main.py`.
3. In the **Advanced Settings**, add your API key to the Secrets:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
4. Click **Deploy**!

---

*Built by Himanshuraj Nimse.*
