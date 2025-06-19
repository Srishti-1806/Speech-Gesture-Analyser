# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from utils.transcriber import transcribe_audio
from utils.body_language import analyze_body_language
from utils.speech_analysis import analyze_speech
from utils.feedback_generator import generate_feedback
from utils.report_generator import generate_pdf_report
from webcam_recorder import record_from_webcam
import uvicorn
from pathlib import Path

app = FastAPI()

class AnalysisResult(BaseModel):
    transcript: str
    speech_score: int
    body_language_score: int
    total_score: int
    feedback: str
    pdf_url: str

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)

    filename = Path(file.filename).name
    file_path = f"temp/{filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    transcript = transcribe_audio(file_path)
    speech_score = analyze_speech(file_path)
    body_language_score = analyze_body_language(file_path)
    feedback = generate_feedback(transcript, speech_score, body_language_score)

    pdf_filename = filename.replace(".mp4", "_report.pdf")
    pdf_path = f"static/reports/{pdf_filename}"
    generate_pdf_report(transcript, speech_score, body_language_score, feedback, pdf_path)

    return AnalysisResult(
        transcript=transcript,
        speech_score=speech_score,
        body_language_score=body_language_score,
        total_score=speech_score + body_language_score,
        feedback=feedback,
        pdf_url=f"/static/reports/{pdf_filename}"
    )

@app.get("/record-webcam", response_model=AnalysisResult)
def record_and_analyze():
    os.makedirs("temp", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)

    video_path = "temp/webcam_recording.mp4"
    record_from_webcam(video_path)

    transcript = transcribe_audio(video_path)
    speech_score = analyze_speech(video_path)
    body_language_score = analyze_body_language(video_path)
    feedback = generate_feedback(transcript, speech_score, body_language_score)

    pdf_filename = "webcam_recording_report.pdf"
    pdf_path = f"static/reports/{pdf_filename}"
    generate_pdf_report(transcript, speech_score, body_language_score, feedback, pdf_path)

    return AnalysisResult(
        transcript=transcript,
        speech_score=speech_score,
        body_language_score=body_language_score,
        total_score=speech_score + body_language_score,
        feedback=feedback,
        pdf_url=f"/static/reports/{pdf_filename}"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
