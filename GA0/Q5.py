import os
import json
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import List

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

# Required for the grader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


class CodeResponse(BaseModel):
    error: List[int]
    result: str


class ErrorAnalysis(BaseModel):
    error_lines: List[int]


def execute_python_code(code: str) -> dict:
    """
    Execute Python and return the exact output.
    AI is NOT used here.
    """
    output_buffer = StringIO()

    try:
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            exec(code, {})

        return {
            "success": True,
            "output": output_buffer.getvalue()
        }

    except Exception:
        # For errors, return the traceback
        return {
            "success": False,
            "output": traceback.format_exc()
        }


def analyze_error_with_ai(code: str, error_traceback: str) -> List[int]:
    """
    Call AI only when Python execution fails.
    """

    # Numbering the code makes line identification much easier
    numbered_code = "\n".join(
        f"{i}: {line}"
        for i, line in enumerate(code.splitlines(), start=1)
    )

    prompt = f"""
You are analyzing a Python execution error.

Identify the exact source-code line number or line numbers responsible
for the error.

NUMBERED PYTHON CODE:
{numbered_code}

TRACEBACK:
{error_traceback}

Return JSON only in exactly this form:

{{"error_lines":[3]}}

Rules:
- error_lines must contain integers only.
- Use the line numbers from the numbered Python code.
- Include only lines directly responsible for the error.
"""

    token = os.environ["AIPIPE_TOKEN"]

    response = requests.post(
        "https://aipipe.org/openrouter/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google/gemini-2.0-flash-lite-001",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "error_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_lines": {
                                "type": "array",
                                "items": {"type": "integer"}
                            }
                        },
                        "required": ["error_lines"],
                        "additionalProperties": False
                    }
                }
            }
        },
        timeout=30
    )

    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]

    # Pydantic structured validation
    result = ErrorAnalysis.model_validate_json(content)

    return result.error_lines


@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(request: CodeRequest):
    execution = execute_python_code(request.code)

    # Successful execution: NEVER call AI
    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    # AI is invoked only after an error
    lines = analyze_error_with_ai(
        request.code,
        execution["output"]
    )

    return {
        "error": lines,
        "result": execution["output"]
    }


@app.get("/")
def home():
    return {"status": "ok"}