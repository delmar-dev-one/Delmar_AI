import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict

import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = Path(os.getenv("AGROVISION_MODELS_DIR", BASE_DIR / "/home/delmar/Downloads/Delmar_AI/Demonstration/projeto-M2/AgroVisionAI_Modulo2_Final.ipynb"))
CNN_PATH = Path(os.getenv("AGROVISION_CNN_PATH", MODELS_DIR / "/home/delmar/Downloads/data_folhas/PlantVillage"))
CLASSES_PATH = Path(os.getenv("AGROVISION_CLASSES_PATH", MODELS_DIR / "classes.json"))
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", 10 * 1024 * 1024))

YOLO_FILES = {
    "v8": Path(os.getenv("YOLO_V8_WEIGHTS", MODELS_DIR / "yolov8_best.pt")),
    "v9": Path(os.getenv("YOLO_V9_WEIGHTS", MODELS_DIR / "yolov9_best.pt")),
    "v11": Path(os.getenv("YOLO_V11_WEIGHTS", MODELS_DIR / "yolo11_best.pt")),
}

state: Dict = {"cnn": None, "classes": [], "yolo": {}, "load_errors": {}}


def load_artifacts():
    state["load_errors"] = {}
    if CNN_PATH.exists() and CLASSES_PATH.exists():
        try:
            state["cnn"] = tf.keras.models.load_model(CNN_PATH)
            state["classes"] = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            state["load_errors"]["cnn"] = str(exc)
            state["cnn"] = None
    else:
        state["load_errors"]["cnn"] = (
            f"Arquivos ausentes: {CNN_PATH.name} e/ou {CLASSES_PATH.name}"
        )

    state["yolo"] = {}
    for version, weights_path in YOLO_FILES.items():
        if weights_path.exists():
            try:
                state["yolo"][version] = YOLO(str(weights_path))
            except Exception as exc:
                state["load_errors"][f"yolo_{version}"] = str(exc)
        else:
            state["load_errors"][f"yolo_{version}"] = f"Pesos não encontrados: {weights_path}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_artifacts()
    yield


app = FastAPI(
    title="AgroVisionAI",
    description="API REST para classificação de folhas e detecção de frutos.",
    version="2.0.0",
    lifespan=lifespan,
)


async def read_image(file: UploadFile) -> np.ndarray:
    allowed = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type and file.content_type.lower() not in allowed:
        raise HTTPException(status_code=415, detail="Envie uma imagem PNG ou JPEG.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Imagem excede o limite de 10 MB.")
    image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Não foi possível decodificar a imagem.")
    return image


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "cnn_loaded": state["cnn"] is not None,
        "classes_loaded": len(state["classes"]) > 0,
        "yolo_loaded": sorted(state["yolo"].keys()),
        "load_errors": state["load_errors"],
    }


@app.post("/classificar-folha")
async def classificar_folha(file: UploadFile = File(...)):
    if state["cnn"] is None:
        raise HTTPException(
            status_code=503,
            detail="CNN indisponível. Treine/exporte o modelo e coloque modelo_folhas.keras e classes.json em models/.",
        )
    image_bgr = await read_image(file)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    input_shape = state["cnn"].input_shape
    height = int(input_shape[1] or 128)
    width = int(input_shape[2] or 128)
    resized = cv2.resize(image_rgb, (width, height)).astype("float32") / 255.0
    probabilities = state["cnn"].predict(np.expand_dims(resized, axis=0), verbose=0)[0]
    class_index = int(np.argmax(probabilities))
    if class_index >= len(state["classes"]):
        raise HTTPException(status_code=500, detail="Mapeamento de classes incompatível com a CNN.")
    confidence = float(probabilities[class_index])
    class_name = state["classes"][class_index]
    healthy = "healthy" in class_name.lower()
    return {
        "arquivo": file.filename,
        "classe_id": class_index,
        "classe": class_name,
        "condicao": "saudavel" if healthy else "possivel_doenca",
        "confianca": round(confidence, 6),
        "observacao": "Predição automatizada; confirme o diagnóstico com avaliação agronômica.",
    }


@app.post("/detectar-fruto")
async def detectar_fruto(
    file: UploadFile = File(...),
    modelo: str = Query("v8", pattern="^(v8|v9|v11)$"),
    confianca_minima: float = Query(0.25, ge=0.0, le=1.0),
):
    detector = state["yolo"].get(modelo)
    if detector is None:
        raise HTTPException(
            status_code=503,
            detail=f"Modelo {modelo} não carregado. Verifique se o peso correspondente está em {MODELS_DIR}.",
        )
    image_bgr = await read_image(file)
    results = detector.predict(source=image_bgr, conf=confianca_minima, verbose=False)
    detections = []
    if results and results[0].boxes is not None:
        for box in results[0].boxes:
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].cpu().tolist()]
            class_id = int(box.cls[0].item())
            detections.append({
                "classe_id": class_id,
                "classe": detector.names.get(class_id, str(class_id)),
                "confianca": round(float(box.conf[0].item()), 6),
                "bbox": {
                    "x1": round(x1, 2), "y1": round(y1, 2),
                    "x2": round(x2, 2), "y2": round(y2, 2),
                },
            })
    return {
        "arquivo": file.filename,
        "modelo": modelo,
        "total_deteccoes": len(detections),
        "deteccoes": detections,
    }


@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    # Erros HTTP previstos continuam sendo tratados pelo FastAPI.
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=500, content={"detail": "Erro interno ao processar a requisição."})
