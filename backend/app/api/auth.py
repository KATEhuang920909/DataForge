from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user
from app.core.database import get_db
from app.schemas import APIResponse, TokenOut, UserLogin, UserCreate, UserPasswordUpdate
from app.services import get_user_by_username, verify_password, create_user, update_user_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=APIResponse)
async def login(body: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "用户名或密码错误")
    if not user.is_active:
        raise HTTPException(403, "用户已被禁用")
    token = create_access_token(user.id, user.role)
    return APIResponse(data=TokenOut(access_token=token).model_dump())


@router.post("/register", response_model=APIResponse)
async def register(body: UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_username(db, body.username)
    if user:
        raise HTTPException(400, "用户名已存在")
    
    new_user = create_user(db, body)
    token = create_access_token(new_user.id, new_user.role)
    return APIResponse(data=TokenOut(access_token=token).model_dump(), message="注册成功")


@router.post("/update-password", response_model=APIResponse)
async def update_password(body: UserPasswordUpdate, db: Session = Depends(get_db)):
    user = get_user_by_username(db, body.username)
    if not user or not verify_password(body.old_password, user.password_hash):
        raise HTTPException(401, "用户名或旧密码错误")
    
    update_user_password(db, user, body.new_password)
    return APIResponse(message="密码修改成功")



@router.get("/me", response_model=APIResponse)
async def me(current_user=Depends(get_current_user)):
    return APIResponse(data={
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    })