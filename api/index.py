import os
import sys

# Ensure the project root is on the import path when running on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # FastAPI instance

# Vercel's Python runtime looks for a top-level callable
handler = app
