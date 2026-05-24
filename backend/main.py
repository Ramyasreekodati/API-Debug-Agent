import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from agents.lower.log_parser import parse_logs
from agents.middle.metrics import compute_metrics
from agents.higher.ai_analyzer import analyze_logs

app = FastAPI(title="API Debug Agent Backend")

@app.post("/upload")
async def upload_log(file: UploadFile = File(...)):
    """Accept a log file, parse it, and store temporarily for session.
    Returns a JSON with parsing status.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    content = await file.read()
    temp_path = os.path.join("temp", file.filename)
    os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(content)
    # parse immediately to validate
    try:
        df = parse_logs(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {e}")
    # store as CSV for later retrieval (simple approach)
    csv_path = temp_path + ".csv"
    df.to_csv(csv_path, index=False)
    return {"message": "File uploaded and parsed", "csv_path": csv_path}

@app.get("/data")
def get_data(csv_path: str):
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Parsed data not found")
    df = pd.read_csv(csv_path)
    return df.to_dict(orient="records")

@app.get("/metrics")
def get_metrics(csv_path: str):
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Parsed data not found")
    df = pd.read_csv(csv_path)
    metrics = compute_metrics(df)
    return metrics

@app.post("/analyze")
async def analyze(csv_path: str):
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Parsed data not found")
    with open(csv_path, "r", encoding="utf-8") as f:
        log_text = f.read()
    analysis = analyze_logs(log_text)
    return {"analysis": analysis}

@app.post("/ingest")
async def ingest_log(log_line: str = Body(..., embed=True)):
    """Accept a raw log line, append it to the master log file, and update the parsed CSV.
    This enables real‑time monitoring by continuously feeding logs.
    """
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    master_path = os.path.join(temp_dir, "master.log")
    # Append the new line
    with open(master_path, "a", encoding="utf-8") as f:
        f.write(log_line.rstrip() + "\n")
    # Re‑parse the entire master log and overwrite CSV
    df = parse_logs(master_path)
    csv_path = master_path + ".csv"
    df.to_csv(csv_path, index=False)
    return {"message": "Log ingested", "csv_path": csv_path}
