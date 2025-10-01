from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI()

# Permitir requisições do app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregue o modelo .pt ou .onnx
# Se preferir usar ONNX, troque para YOLO("best.onnx")
model = YOLO("best.pt")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    img = Image.open(io.BytesIO(image_bytes))
    results = model(img)
    # Pega a classe com maior confiança
    if results and results[0].boxes:
        class_id = int(results[0].boxes.cls[0])
        conf = float(results[0].boxes.conf[0])
        class_name = results[0].names[class_id]
        return {"class": class_name, "confidence": conf}
    return {"class": "unknown", "confidence": 0}