from fastapi import APIRouter, HTTPException, Depends
from app.schemas.users import UserCreate, UserResponse
from app.services.user_service import UserService
from app.dependencies import get_user_service

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
def list_users(user_service: UserService = Depends(get_user_service)):
    """
    List all users.
    """
    users = user_service.list_users()
    return users


@router.post("/", response_model=UserResponse)
def create_user(request: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    Create a new user.
    """
    try:
        user = user_service.create_user(request)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """
    Retrieve a user by their ID.
    """
    try:
        user = user_service.get_user(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
