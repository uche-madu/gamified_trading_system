from pydantic import BaseModel, ConfigDict, Field


# Request schema for creating a user
class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username must be between 3 and 50 characters.",
    )


# Response schema for user data
class UserResponse(BaseModel):
    id: int
    username: str
    gem_count: int
    rank: int | None = None
    balance: float
    trade_count: int

    model_config = ConfigDict(from_attributes=True)


# Schema for deposit and withdrawal operations
class BalanceOperation(BaseModel):
    user_id: int = Field(..., gt=0, description="User ID must be a positive integer.")
    amount: float = Field(..., gt=0, description="Amount must be greater than zero.")
