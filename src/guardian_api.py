from fastapi import FastAPI
from pydantic import BaseModel
from guardian_extended import guardian_session

app = FastAPI(title="CANDELA Guardian API")

class Prompt(BaseModel):
    text: str

class Answer(BaseModel):
    response: str
    directive_hash: str

@app.post("/ask", response_model=Answer)
def ask(prompt: Prompt):
    result_text, d_hash = guardian_session(prompt.text)
    return {"response": result_text, "directive_hash": d_hash}
