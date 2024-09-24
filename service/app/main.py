from contextlib import asynccontextmanager
from app.app_logger import appLogger
from threading import Thread
from app.db import get_db_session
from app.env import EC2_IP_ADDRESS
from app.sqs_consumer import process_sqs_messages
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    appLogger.debug("[EmailSnap]Starting the application")
    daemon_thread = Thread(target=process_sqs_messages, daemon=True)
    daemon_thread.start()
    
    yield
    
    appLogger.debug("[EmailSnap]Shutting down the application")

app = FastAPI(lifespan=lifespan)


@app.get("/analytics/{path:path}")
async def analytics_redirect(path: str):
    if EC2_IP_ADDRESS:
        return RedirectResponse(url=f"http://{EC2_IP_ADDRESS}:3000/{path}")
    else:
        return RedirectResponse(url=f"http://localhost:3000/{path}")

@app.get("/ping")
def health_check():
    return {"message": "pong"}