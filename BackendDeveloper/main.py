from fastapi import (
    FastAPI,
    Depends,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from BackendDeveloper.database import Base, engine, get_db
from BackendDeveloper.models import User
from BackendDeveloper.schemas import RegisterRequest, LoginRequest
from BackendDeveloper.schemas import AuthResponse, AvatarResponse, DeleteResponse
from BackendDeveloper.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    decode_token,
)
from BackendDeveloper.utils import save_avatar, delete_avatar
from BackendDeveloper.jsend import success, fail

from BackendDeveloper.ws_manager import WebSocketManager

ws_manager = WebSocketManager()

import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB tables
Base.metadata.create_all(bind=engine)

# Serve static avatar files
app.mount("/static", StaticFiles(directory="BackendDeveloper/static"), name="static")

ALLOWED_AVATAR_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}  # (not sure if it works for all - will test later)
MIN_PASSWORD_LENGTH = 6  # can make it more strict later


# ===========================
# AUTH ROUTES
# ===========================


@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if len(data.password) < MIN_PASSWORD_LENGTH:
        return fail(
            {"password": f"Password must be at least {MIN_PASSWORD_LENGTH} characters"}
        )

    existing = db.query(User).filter(User.identifier == data.identifier).first()
    if existing:
        return fail({"identifier": "Already taken"})

    user = User(
        identifier=data.identifier,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return success(AuthResponse(access_token=token).dict())


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.identifier == data.identifier).first()
    if not user or not verify_password(data.password, user.password_hash):
        return fail({"credentials": "Invalid identifier or password"})

    token = create_access_token({"sub": str(user.id)})

    return success(AuthResponse(access_token=token).dict())


# ===========================
# AVATAR ROUTES
# ===========================


@app.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_AVATAR_EXTENSIONS)}",
        )

    # Save file
    try:
        avatar_url = save_avatar(user.id, file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save avatar: {str(e)}")

    # Update DB
    user.avatar_url = avatar_url
    db.commit()

    # Notify user WebSocket(s)
    # this was also not happening for several reasons
    # implemented await and then it worked
    await ws_manager.send_user(user.id, "Avatar updated")

    return success(AvatarResponse(avatar_url=avatar_url).dict())


@app.get("/me/avatar")
def get_my_avatar(user: User = Depends(get_current_user)):
    url = user.avatar_url or "/static/avatars/default.png"
    return success(AvatarResponse(avatar_url=url).dict())


# ===========================
# WEBSOCKET ENDPOINT
# ===========================


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str):
    try:
        decoded = decode_token(token)
        user_id = int(decoded["sub"])
    except:
        await ws.close()
        return

    await ws_manager.connect(user_id, ws)

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(user_id, ws)


# ===========================
# DELETE USER
# ===========================


@app.delete("/user")
async def delete_user(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    delete_avatar(user.id)

    db.delete(user)
    db.commit()

    # Close the active WebSocket(s)
    # Had the same issue in @app.post ("/avatar")
    # using await fixed the probelm
    await ws_manager.send_user(user.id, "User deleted")

    return success(DeleteResponse(message="User deleted").dict())
