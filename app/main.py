from fastapi import FastAPI

from app.presentation.routers import auth, users


app = FastAPI(
    title="User-service",
    version="0.1.0",
)


app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/health_check", tags=["Health Check"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readiness_check", tags=["Readiness Check"])
async def readiness_check() -> dict[str, str]:
    return {"status": "ready"}
