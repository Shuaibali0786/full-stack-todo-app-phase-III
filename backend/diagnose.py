"""
Diagnostic script to check middleware configuration and environment
"""
import sys
import os

print("=" * 60)
print("ENVIRONMENT DIAGNOSTIC")
print("=" * 60)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print()

print("=" * 60)
print("CHECKING FASTAPI/STARLETTE VERSIONS")
print("=" * 60)
try:
    import fastapi
    print(f"FastAPI version: {fastapi.__version__}")
    print(f"FastAPI location: {fastapi.__file__}")
except Exception as e:
    print(f"FastAPI import error: {e}")

try:
    import starlette
    print(f"Starlette version: {starlette.__version__}")
    print(f"Starlette location: {starlette.__file__}")
except Exception as e:
    print(f"Starlette import error: {e}")

print()
print("=" * 60)
print("CHECKING SSE-STARLETTE")
print("=" * 60)
try:
    import sse_starlette
    print(f"sse-starlette version: {sse_starlette.__version__}")
    print(f"sse-starlette location: {sse_starlette.__file__}")
except Exception as e:
    print(f"sse-starlette import error: {e}")

print()
print("=" * 60)
print("ATTEMPTING TO LOAD APP")
print("=" * 60)
try:
    from src.main import app
    print("[SUCCESS] App loaded successfully!")
    print(f"App type: {type(app)}")
    print(f"App title: {app.title}")
    print(f"Number of routes: {len(app.routes)}")
    print(f"Middleware stack: {len(app.user_middleware)} user middleware")
    print()
    print("Middleware details:")
    for idx, middleware in enumerate(app.user_middleware):
        print(f"  {idx + 1}. {middleware}")
except Exception as e:
    print("[FAILED] App load FAILED!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
