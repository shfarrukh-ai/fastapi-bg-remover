from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from rembg import remove
from PIL import Image
import io

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Background Remover API Running"}

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents)).convert("RGBA")

        output_bytes = remove(contents)
        output_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        return JSONResponse({
            "filename": file.filename,
            "message": "Background removed successfully",
            "output_image_base64": img_byte_arr.hex()
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
