import json
import math
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

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
            row for row in data
            if row["region"] == region
        ]

        latencies = [row["latency_ms"] for row in rows]
        uptimes = [row["uptime_pct"] for row in rows]

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

    return results