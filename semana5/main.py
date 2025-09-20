from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

import auth
import models
from database import SessionLocal, engine
from schemas import UserRegister, UserLogin, UserResponse, Token, PostCreate, PostResponse

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Lista simple para posts (simulación)
posts = []

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- Usuarios -----------------
@app.post("/register", response_model=UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    if auth.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username ya está registrado")

    user = auth.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=True
    )

@app.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o password incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(user.username)
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )

# ----------------- Endpoints de prueba -----------------
@app.get("/protected")
def protected_endpoint(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "message": f"Hola {current_user.username}, tienes acceso!",
        "user_id": current_user.id,
        "status": "authenticated"
    }

@app.get("/public")
def public_endpoint():
    return {
        "message": "Este endpoint es público",
        "status": "no authentication required"
    }

# ----------------- Posts -----------------
@app.post("/posts", response_model=PostResponse)
def create_post(post_data: PostCreate, current_user: models.User = Depends(auth.get_current_user)):
    new_post = {
        "id": len(posts) + 1,
        "title": post_data.title,
        "content": post_data.content,
        "author": current_user.username
    }
    posts.append(new_post)
    return PostResponse(**new_post)

@app.get("/posts", response_model=List[PostResponse])
def get_posts():
    return [PostResponse(**post) for post in posts]

@app.get("/posts/my", response_model=List[PostResponse])
def get_my_posts(current_user: models.User = Depends(auth.get_current_user)):
    my_posts = [post for post in posts if post["author"] == current_user.username]
    return [PostResponse(**post) for post in my_posts]

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, current_user: models.User = Depends(auth.get_current_user)):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    if post["author"] != current_user.username:
        raise HTTPException(status_code=403, detail="No tienes permiso para borrar este post")
    posts.remove(post)
    return {"message": "Post eliminado exitosamente"}
