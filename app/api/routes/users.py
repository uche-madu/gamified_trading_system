from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_service
from app.schemas.users import BalanceOperation, UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
def list_users(user_service: UserService = Depends(get_user_service)):
    """
    List all users.
    """
    users = user_service.list_users()
    return users


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    request: UserCreate, user_service: UserService = Depends(get_user_service)
):
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


@router.post("/deposit", status_code=204)
def deposit_balance(
    request: BalanceOperation, user_service: UserService = Depends(get_user_service)
):
    """
    Deposit an amount into the user's balance.
    """
    try:
        user_service.deposit_balance(user_id=request.user_id, amount=request.amount)
        return {"detail": "Deposit successful."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw", status_code=204)
def withdraw_balance(
    request: BalanceOperation, user_service: UserService = Depends(get_user_service)
):
    """
    Withdraw an amount from the user's balance.
    """
    try:
        user_service.withdraw_balance(user_id=request.user_id, amount=request.amount)
        return {"detail": "Withdrawal successful."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
