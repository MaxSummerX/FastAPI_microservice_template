from fastapi import FastAPI


app = FastAPI(
    title="User-service",
    version="0.1.0",
)


@app.get("/health_check", tags=["Health Check"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readiness_check", tags=["Readiness Check"])
async def readiness_check() -> dict[str, str]:
    return {"status": "ready"}
