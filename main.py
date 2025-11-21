from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from rembg import remove
from PIL import Image
import io

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Background Remover API is running!"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # Read file bytes
    input_bytes = await file.read()

    # Process background removal
    output_bytes = remove(input_bytes)

    return Response(content=output_bytes, media_type="image/png")
