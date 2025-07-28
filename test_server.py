#!/usr/bin/env python3
"""
Script para probar si el servidor responde.
"""
import requests

try:
    response = requests.get("http://localhost:8000/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print("✅ Servidor está funcionando correctamente!")
except Exception as e:
    print(f"❌ Error conectando al servidor: {e}") 