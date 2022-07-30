from fastapi import FastAPI, Request, HTTPException
from mangum import Mangum
from starlette.responses import JSONResponse

from blackangus.routers.v1 import line
from blackangus.scrappers.v1.line import LineScrapperException

app = FastAPI(
    title="Black Angus Lambda",
    description="Lambda Scrapper for Black Angus Bot",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

app.include_router(line.router)


@app.exception_handler(LineScrapperException)
async def line_scrapper_exception_handler(
    _: Request,
    exc: LineScrapperException,
):
    return JSONResponse(
        status_code=500,
        content={"result": {"success": False, "message": str(exc)}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": {"success": False, "message": exc.detail}},
    )


handler = Mangum(app, lifespan="off")
