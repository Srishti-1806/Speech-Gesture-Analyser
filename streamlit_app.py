import streamlit as st
import os
import tempfile
from datetime import datetime
from pipeline import run_analysis_pipeline

st.title("🔊📹 Speech & Body Language Analyzer")

video_file = st.file_uploader("Upload a video for analysis", type=["mp4", "mov", "avi"])

if video_file is not None:
    # Ensure the folder exists
    os.makedirs("temp", exist_ok=True)

    # Save uploaded file temporarily
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = f"temp/input_{t}.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    st.success("Video uploaded successfully.")

    if st.button("Run Analysis"):
        st.info("Analyzing... please wait")
        pdf_path = run_analysis_pipeline(video_path)
        st.success("Analysis complete!")
        st.download_button("📄 Download Report", data=open(pdf_path, "rb"), file_name="analysis_report.pdf")
