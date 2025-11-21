from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from rembg import remove
from PIL import Image
import numpy as np
import io

app = FastAPI(title="Background Remover API")

@app.get("/")
def home():
    return {"status": "API is running successfully!", "message": "Upload an image to remove background."}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Read image
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Background removal
        output = remove(np.array(input_image))
        output_image = Image.fromarray(output)

        # Save output
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        return FileResponse(output_buffer, media_type="image/png", filename="output.png")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
