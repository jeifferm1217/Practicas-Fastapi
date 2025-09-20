from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
import warnings

# Evitar warnings molestos en tests
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from .database import engine, Base, get_db
from .models import User, Proyecto
from .schemas import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    ProyectoCreate,
    ProyectoResponse,
)
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
)

# --- Inicialización de la app ---
app = FastAPI()

# Router para proyectos
router = APIRouter(prefix="/garden")

# -----------------
# Endpoints de Autenticación
# -----------------
@app.post("/register", response_model=UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login_for_access_token(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/protected")
def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you are authenticated."}


@app.get("/admin-only")
def admin_only_endpoint(current_user: User = Depends(require_admin)):
    return {"message": "Welcome, Admin. This is a restricted area."}


# -----------------
# Endpoints de Proyectos (CRUD)
# -----------------
@router.post("/proyectos/", response_model=ProyectoResponse, status_code=status.HTTP_201_CREATED)
def create_proyecto(
    proyecto_data: ProyectoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_proyecto = Proyecto(
        **proyecto_data.model_dump(),
        creado_por_id=current_user.id,
    )
    db.add(db_proyecto)
    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto


@router.get("/proyectos/", response_model=List[ProyectoResponse])
def get_proyectos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proyectos = db.query(Proyecto).all()
    return proyectos


@router.get("/proyectos/{proyecto_id}", response_model=ProyectoResponse)
def get_proyecto_by_id(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not db_proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return db_proyecto


@router.put("/proyectos/{proyecto_id}", response_model=ProyectoResponse)
def update_proyecto(
    proyecto_id: int,
    proyecto_data: ProyectoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not db_proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    if db_proyecto.creado_por_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para actualizar este proyecto"
        )

    for key, value in proyecto_data.model_dump().items():
        setattr(db_proyecto, key, value)

    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto


@router.delete("/proyectos/{proyecto_id}", status_code=status.HTTP_200_OK)
def delete_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not db_proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    if db_proyecto.creado_por_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permisos para eliminar este proyecto"
        )

    db.delete(db_proyecto)
    db.commit()
    return {"message": "Proyecto eliminado exitosamente."}


# -----------------
# Registrar el router al final
# -----------------
app.include_router(router)
