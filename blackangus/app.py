from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from blackangus.routers.v1 import line
from blackangus.scrappers.v1.line import LineScrapperException

app = FastAPI(
    title="Black Angus Lambda",
    description="Lambda Scrapper for Black Angus Bot",
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
