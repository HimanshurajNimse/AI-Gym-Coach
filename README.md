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

If you intend to deploy this app to Streamlit Community Cloud or any other cloud provider, you **must configure a TURN server** for the WebRTC camera to connect over the internet.
1. Create a free [Twilio](https://www.twilio.com/) account.
2. Add `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` to your Streamlit Secrets.
3. Update `main.py`'s `rtc_configuration` to fetch ice servers using Twilio's Network Traversal Service.

---

*Built by Himanshuraj Nimse.*
