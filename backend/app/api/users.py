from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_admin, get_current_user
from app.core.database import get_db
from app.schemas import APIResponse, UserCreate, UserUpdate, UserOut, UserPasswordUpdate
from app.services import create_user, delete_user, get_user_by_id, list_users, update_user, verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


def _u(u) -> dict:
    return UserOut.model_validate(u).model_dump()


@router.get("/", response_model=APIResponse)
async def list_all(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=200), db: Session = Depends(get_db), current_user=Depends(require_admin)):
    items, total = list_users(db, page, size)
    return APIResponse(data={
        "items": [_u(u) for u in items],
        "total": total, "page": page, "page_size": size,
        "pages": (total + size - 1) // size,
    })


@router.post("/", response_model=APIResponse)
async def create(body: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    try:
        user = create_user(db, body)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return APIResponse(message="用户创建成功", data=_u(user))


@router.get("/{user_id}", response_model=APIResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "用户不存在")
    return APIResponse(data=_u(user))


@router.patch("/{user_id}", response_model=APIResponse)
async def patch_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = update_user(db, user_id, body)
    if not user:
        raise HTTPException(404, "用户不存在")
    return APIResponse(message="用户更新成功", data=_u(user))


@router.delete("/{user_id}", response_model=APIResponse)
async def remove_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if not delete_user(db, user_id):
        raise HTTPException(404, "用户不存在")
    return APIResponse(message="用户已删除")


@router.patch("/me/password", response_model=APIResponse)
async def update_my_password(body: UserPasswordUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not verify_password(body.old_password, current_user.password_hash):
        raise HTTPException(400, "旧密码错误")
    
    hashed_password = get_password_hash(body.new_password)
    update_user(db, current_user.id, UserUpdate(password=hashed_password))
    return APIResponse(message="密码更新成功")