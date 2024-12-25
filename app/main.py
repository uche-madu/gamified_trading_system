from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import assets, leaderboard, portfolios, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Performs initialization and cleanup tasks for the FastAPI application.
    """
    # No need to call init_db(), as Alembic manages the database schema.
    yield
    # Perform any cleanup tasks if needed (e.g., closing connections, files)
    # For this project, no specific cleanup is needed.


# Initialize FastAPI application with lifespan
app = FastAPI(lifespan=lifespan)

# Include API routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(portfolios.router, prefix="/portfolios", tags=["Portfolios"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])


@app.get("/")
def root():
    """
    Basic welcome endpoint.
    """
    return {"message": "Welcome to the Gamified Trading System"}


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
