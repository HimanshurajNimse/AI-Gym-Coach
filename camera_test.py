import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode

st.set_page_config(page_title="WebRTC Camera Test")

st.title("WebRTC Camera Test")

ctx = webrtc_streamer(
    key="camera-test",
    mode=WebRtcMode.SENDRECV,
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
)

st.write("Playing:", ctx.state.playing)
st.write("Signalling:", ctx.state.signalling)