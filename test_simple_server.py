#!/usr/bin/env python3
"""
Script simple para probar el servidor webhook.
"""
import uvicorn
from fastapi import FastAPI

# Crear una app simple para probar
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 