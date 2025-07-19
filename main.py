#!/usr/bin/env python3
"""
Main entry point for Sannetic Explorer

Starts the FastAPI application with the restructured package.
"""

import uvicorn
from sannetic_explorer.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 