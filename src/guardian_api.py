try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as e:
    raise SystemExit(
        "FastAPI extras are not installed. Install with: pip install fastapi uvicorn pydantic"
    ) from e

from .guardian_runtime import guardian_chat
from .guardian_prototype import _load_directives, _bundle_hash

app = FastAPI(title="CANDELA Guardian API")

class Prompt(BaseModel):
    text: str

class Answer(BaseModel):
    response: dict
    directive_hash: str

@app.post("/ask", response_model=Answer)
def ask(prompt: Prompt):
    result = guardian_chat(prompt.text)
    directives = _load_directives()
    d_hash = _bundle_hash(directives)
    return {"response": result, "directive_hash": d_hash}
