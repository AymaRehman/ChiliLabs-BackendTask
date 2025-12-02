import os
from fastapi import UploadFile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")

# --- FIX FOR ONEDRIVE / ICLOUD ---
# If the path exists but is NOT a directory, delete it
if os.path.exists(AVATAR_DIR) and not os.path.isdir(AVATAR_DIR):
    os.remove(AVATAR_DIR)

# If directory does NOT exist, create it
if not os.path.isdir(AVATAR_DIR):
    os.makedirs(AVATAR_DIR)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def save_avatar(user_id: int, file: UploadFile) -> str:
    """
    Save avatar for user. Automatically deletes previous avatar files.
    Returns public URL for client.
    """
    # Delete old avatars
    delete_avatar(user_id)

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file type: {file_ext}")

    filename = f"{user_id}{file_ext}"
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return f"/static/avatars/{filename}"


def delete_avatar(user_id: int):
    """
    Delete any avatar files for the user.
    """
    for ext in ALLOWED_EXTENSIONS:
        path = os.path.join(AVATAR_DIR, f"{user_id}{ext}")
        if os.path.exists(path):
            os.remove(path)
