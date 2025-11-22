# =====================
# main.py
# =====================
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from rembg import remove

app = FastAPI(title="Background Remover API")

@app.get("/")
def home():
    return {"status": "API is running"}

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        input_bytes = await file.read()
        output_bytes = remove(input_bytes)
        return Response(content=output_bytes, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}
