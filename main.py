from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from database.db import engine, Base, SessionLocal
from websocket.manager import ConnectionManager
from models.message import MessageDB
from routes.chat import router as chat_router
from auth.routes import router as auth_router

from jose import jwt, JWTError

# ==============================
# CONFIG
# ==============================
SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

# ==============================
# APP INIT
# ==============================
app = FastAPI()
manager = ConnectionManager()

# ==============================
# INCLUDE ROUTES
# ==============================
app.include_router(chat_router)
app.include_router(auth_router)

# ==============================
# CREATE TABLES ON STARTUP
# ==============================
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ==============================
# SERVE FRONTEND (HTML)
# ==============================
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as file:
        return file.read()

# ==============================
# TOKEN VERIFICATION
# ==============================
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# ==============================
# WEBSOCKET ENDPOINT (SECURED)
# ==============================
@app.websocket("/ws/{room_id}/{token}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str):
    username = verify_token(token)

    if not username:
        await websocket.close()
        return

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            async with SessionLocal() as session:
                msg = MessageDB(username=username, content=data, room_id=room_id)
                session.add(msg)
                await session.commit()

            await manager.broadcast(
                f"[{room_id}] {username}: {data}",
                sender=websocket
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)