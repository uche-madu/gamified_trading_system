from fastapi import APIRouter, Depends, HTTPException
from app.schemas.leaderboard import LeaderboardEntry
from app.services.ranking_service import RankingService
from app.dependencies import get_ranking_service

router = APIRouter()

@router.get("/", response_model=list[LeaderboardEntry])
def get_leaderboard(top_n: int = 10, ranking_service: RankingService = Depends(get_ranking_service)):
    """
    Retrieve the leaderboard with the top N users based on gem count.
    """
    try:
        # Assign ranks and get top users
        ranking_service.assign_ranks()
        top_users = ranking_service.get_top_n_users(top_n)

        # Convert to response schema
        return [
            LeaderboardEntry(
                rank=user.rank,
                username=user.username,
                gem_count=user.gem_count,
            )
            for user in top_users
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while generating the leaderboard.")
