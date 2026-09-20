import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, WebRtcMode

st.set_page_config(page_title="WebRTC Resize Test")

st.title("WebRTC Resize Test")


components.html(
    """
    <script>
        setTimeout(() => {
            window.parent.dispatchEvent(new Event("resize"));
        }, 500);
    </script>
    """,
    height=0,
)


ctx = webrtc_streamer(
    key="resize-test",
    mode=WebRtcMode.SENDRECV,
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
)

st.write("Playing:", ctx.state.playing)
st.write("Signalling:", ctx.state.signalling)