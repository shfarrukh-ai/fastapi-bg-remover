# =====================
# main.py (Render compatible, no ONNX)
# =====================
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from PIL import Image
import numpy as np
import cv2
import io

app = FastAPI(title="CPU Background Remover")

# ----------------------------
# Helper functions (grabcut-based)
# ----------------------------
def pil_to_bgr(p: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(p.convert("RGB")), cv2.COLOR_RGB2BGR)

def resize_preserve_aspect(p: Image.Image, target_w: int):
    w, h = p.size
    if w <= target_w: return p.copy(), 1.0
    scale = target_w / w
    new_h = max(1,int(h*scale))
    return p.resize((target_w,new_h), Image.LANCZOS), scale

def run_grabcut_once(bgr: np.ndarray):
    mask = np.zeros(bgr.shape[:2], np.uint8)
    rect = (1,1,bgr.shape[1]-2,bgr.shape[0]-2)
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)
    cv2.grabCut(bgr, mask, rect, bgdModel, fgdModel,1,cv2.GC_INIT_WITH_RECT)
    out = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    return out

def mask_to_alpha(mask: np.ndarray):
    return mask.astype(np.uint8)

# ----------------------------
@app.get("/")
def home():
    return {"status": "CPU Background Remover API Running"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents)).convert("RGB")
        preview, _ = resize_preserve_aspect(input_image, 320)
        bgr = pil_to_bgr(preview)
        mask = run_grabcut_once(bgr)

        rgba = np.dstack([np.array(preview), mask])
        output_image = Image.fromarray(rgba, "RGBA")

        buf = io.BytesIO()
        output_image.save(buf, format='PNG')
        return Response(content=buf.getvalue(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
