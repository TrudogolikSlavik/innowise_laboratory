from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck() -> dict:
    """
    Docstring for healthcheck
    
    :return: Description
    :rtype: dict
    """
    return {"status": "ok"}
