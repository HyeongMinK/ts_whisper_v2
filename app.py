import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, AudioProcessorBase
import whisper
import soundfile as sf
import numpy as np
import tempfile

# Load the Whisper model
model = whisper.load_model("base")

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_frames = []

    def recv_queued(self, frames):
        for frame in frames:
            self.audio_frames.append(frame.to_ndarray().flatten())
        return frames

    def get_audio_frames(self):
        return self.audio_frames

# Streamlit interface
st.title("Audio Recording and Transcription with Whisper")

st.write("Record your audio and transcribe it to text.")

# WebRTC Streamer for recording audio
webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"audio": True, "video": False},
    audio_processor_factory=AudioProcessor,
    async_processing=True,
)

# Placeholder for the transcription
transcription_placeholder = st.empty()

if webrtc_ctx.state.playing:
    st.write("Recording... Click the stop button to finish.")

if webrtc_ctx.state.playing is False and webrtc_ctx.audio_processor:
    # Retrieve audio frames
    audio_frames = webrtc_ctx.audio_processor.get_audio_frames()
    
    if audio_frames:
        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav_file:
            sf.write(tmp_wav_file.name, np.concatenate(audio_frames), 16000)
            tmp_wav_file.flush()

            # Transcribe audio using Whisper
            transcription = model.transcribe(tmp_wav_file.name)
            transcription_text = transcription['text']
            
            # Display the transcription
            transcription_placeholder.text_area("Transcription", transcription_text)
