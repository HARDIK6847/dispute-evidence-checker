from fastapi import FastAPI
from models import CaseRequest
from analyzer import analyze

app = FastAPI(
    title="Dispute Evidence Checker",
    description="Prototype for detecting contradictions and evidence gaps across dispute documents.",
    version="0.1.0",
)


@app.get("/")
def health():
    return {"status": "ok", "service": "dispute-evidence-checker"}


@app.post("/analyze")
def analyze_case(case: CaseRequest):
    return analyze(case.documents)
