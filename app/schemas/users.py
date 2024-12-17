from pydantic import BaseModel, ConfigDict

# Request schema for creating a user
class UserCreate(BaseModel):
    user_id: int
    username: str

# Response schema for user data
class UserResponse(BaseModel):
    id: int
    username: str
    gem_count: int
    rank: int | None = None 

    model_config = ConfigDict(from_attributes=True)