from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck() -> dict:
    """Return health status of the API service."""
    return {"status": "ok"}
