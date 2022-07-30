import asyncio

import pytest
from fastapi import HTTPException
from pytest_httpx import HTTPXMock

from blackangus.scrappers.v1.line import LineEmoticonScrapper, LineScrapperException


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


LINE_404_HTML = """
<!DOCTYPE html>
<html lang="ko" data-lang="ko">
    <head></head>
    <body></body>
</html>
"""


@pytest.mark.asyncio
async def test_scrap_with_invalid_line_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        html=LINE_404_HTML,
        text=LINE_404_HTML,
        status_code=404,
    )

    scrapper = LineEmoticonScrapper()

    with pytest.raises(HTTPException):
        await scrapper.scrap(-1)


@pytest.mark.asyncio
async def test_scrap_with_region_blocked_id():
    scrapper = LineEmoticonScrapper()

    with pytest.raises(LineScrapperException):
        # This Emoticon ID is blocked in other region except Japan. ;)
        await scrapper.scrap(19921174)


@pytest.mark.asyncio
async def test_valid_scrap():
    scrapper = LineEmoticonScrapper()
    result = await scrapper.scrap(570)

    assert result.item_id == 570
    assert result.author == "LINE"
    assert len(result.items) == 40
