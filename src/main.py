from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/logo.png")
async def plugin_logo():
    filename = os.path.join('static', 'logo.png')
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest(request: Request):
    host = request.client.host
    with open(os.path.join(os.path.dirname(__file__), "../.well-known", "ai-plugin.json")) as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(content=text, media_type="application/json")

@app.get("/openapi.yaml")
async def openapi_spec(request: Request):
    host = request.client.host
    with open(os.path.join(os.path.dirname(__file__), "..", "openapi.yaml")) as f:
        text = f.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return Response(content=text, media_type="text/yaml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

