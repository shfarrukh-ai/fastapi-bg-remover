from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from rembg import remove
from PIL import Image
import io

app = FastAPI()

# Template folder mount
templates = Jinja2Templates(directory="templates")

# Static files (CSS/JS if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------------------
# 1️⃣ Home Page (index.html)
# ---------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------
# 2️⃣ Background Remover API
# ---------------------------
@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents))

        # Remove background
        output_image = remove(input_image)

        # Save to bytes
        img_bytes = io.BytesIO()
        output_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Return processed image
        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
