#!/bin/bash
# cd backend
# exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
