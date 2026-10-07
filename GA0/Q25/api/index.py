import json
import math
from pathlib import Path
from typing import List

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Explicit OPTIONS handler
@app.options("/api")
def options_api():
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

# Load JSON data
DATA_FILE = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: float


def percentile_95(values):
    values = sorted(values)

    if not values:
        return None

    pos = 0.95 * (len(values) - 1)

    lower = math.floor(pos)
    upper = math.ceil(pos)

    if lower == upper:
        return values[lower]

    return values[lower] + (
        values[upper] - values[lower]
    ) * (pos - lower)


@app.post("/api")
def latency_stats(body: RequestBody):
    results = {}

    for region in body.regions:
        rows = [
            row
            for row in data
            if row["region"] == region
        ]

        latencies = [
            row["latency_ms"]
            for row in rows
        ]

        uptimes = [
            row["uptime_pct"]
            for row in rows
        ]

        if not rows:
            results[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            }
            continue

        results[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": percentile_95(latencies),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(
                1
                for latency in latencies
                if latency > body.threshold_ms
            ),
        }

    return Response(
        content=json.dumps(results),
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*"
        },
    )


@app.get("/")
def home():
    return {
        "status": "ok"
    }