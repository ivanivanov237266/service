from fastapi import FastAPI
from api.routes import router
import logging
import sys
from config import settings

# Configure structured logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "module":"%(name)s", "message":"%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI(title="LLM Summarization Service")
app.include_router(router, prefix="/api/v1")


#poka
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)