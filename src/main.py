import io
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

PORT = 8000


HOSTNAME = "https://speak-gpt-rust.vercel.app"

def load_env_vars():
    if os.path.isfile(os.path.join(os.path.dirname(__file__), "../.env")):
        from dotenv import load_dotenv
        load_dotenv()
    
    if os.getenv("env") == "dev":
        global HOSTNAME
        HOSTNAME = f"http://localhost:{PORT}"

load_env_vars()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def hello():
    return {"message": "Hello, from a Python REST API!"}

class IncomingText(BaseModel):
    text: str

def text_to_speech(text: str):
    voice_id = "EXAVITQu4vr4xnSDxMaL"
    api_key = ""

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        # "xi-api-key": "<xi-api-key>"
    }

    data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }

    response = requests.post(url, json=data, headers=headers)
    return response.content if response.status_code == 200 else None

@app.post("/speak")
async def speak(text: IncomingText):
    audio_data = text_to_speech(text.text)
    if audio_data is not None:
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=400, detail="Text to speech conversion failed")


@app.get("/logo.png")
async def plugin_logo():
    filename = os.path.join('static', 'logo.png')
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest(request: Request):
    with open(os.path.join(os.path.dirname(__file__), "../.well-known", "ai-plugin.json")) as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", HOSTNAME)
        return Response(content=text, media_type="application/json")

@app.get("/openapi.yaml")
async def openapi_spec(request: Request):
    with open(os.path.join(os.path.dirname(__file__), "..", "openapi.yaml")) as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", HOSTNAME)
        return Response(content=text, media_type="text/yaml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT)

