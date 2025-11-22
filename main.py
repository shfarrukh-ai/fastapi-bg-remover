from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np
import cv2
import io
import os

app = FastAPI(title="CPU Background Remover")

# Mount static folder for CSS/JS/images
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve HTML interface from templates folder
@app.get("/", response_class=HTMLResponse)
async def home_page():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Background removal endpoint
@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    contents = await file.read()
    input_image = Image.open(io.BytesIO(contents)).convert("RGB")

    # CPU-based GrabCut for preview
    w, h = input_image.size
    scale = 320 / w if w > 320 else 1.0
    new_h = int(h * scale)
    preview = input_image.resize((int(w*scale), new_h), Image.LANCZOS)
    bgr = cv2.cvtColor(np.array(preview), cv2.COLOR_RGB2BGR)

    mask = np.zeros(bgr.shape[:2], np.uint8)
    rect = (1, 1, bgr.shape[1]-2, bgr.shape[0]-2)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgdModel, fgdModel, 1, cv2.GC_INIT_WITH_RECT)
    mask = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD), 255, 0).astype(np.uint8)

    rgba = np.dstack([np.array(preview), mask])
    output_image = Image.fromarray(rgba, "RGBA")

    buf = io.BytesIO()
    output_image.save(buf, format='PNG')
    return Response(content=buf.getvalue(), media_type="image/png")

# Run command on Render:
# uvicorn main:app --host 0.0.0.0 --port $PORT
