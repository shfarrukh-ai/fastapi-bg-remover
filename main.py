from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from rembg import remove, new_session

app = FastAPI(
    title="Background Remover API",
    description="Fast, lightweight background removal API for Fiverr/Clients.",
    version="1.0.0"
)

# Lightweight model (9MB)
session = new_session("u2netp")

@app.get("/")
def home():
    return {"status": "OK", "message": "Background remover running..."}

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        output = remove(image_bytes, session=session)
        return Response(content=output, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}
