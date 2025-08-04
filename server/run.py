#!/usr/bin/env python3
"""
Simple run script for local development.
Run this script to start the voice agent server locally.
"""

import uvicorn
from app.config import Config

if __name__ == "__main__":
    print("Starting Voice Agent Server...")
    print(f"Host: {Config.HOST}")
    print(f"Port: {Config.PORT}")
    print(f"Debug: {Config.DEBUG}")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    ) 