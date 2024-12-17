from pydantic import BaseModel, ConfigDict

# Response schema for leaderboard entries
class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    gem_count: int

    model_config = ConfigDict(from_attributes=True)