import asyncio

import orjson
import pytest
from fastapi import HTTPException
from pytest_httpx import HTTPXMock

from blackangus.routers.v1.line import search_list_route, fetch_info_route


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_search_with_empty_keyword():
    with pytest.raises(HTTPException) as exception_info:
        await search_list_route()

    assert exception_info.value.status_code == 400
    assert exception_info.value.detail == "'keyword' query field must be not empty."


LINE_MOCKED_BODY = orjson.loads(
    """
{
  "totalCount": 34,
  "items": [
    {
      "id": "-10",
      "title": "테스트 1",
      "description": null,
      "newFlag": false,
      "productUrl": "/stickershop/product/-10/ko",
      "type": "STICKER",
      "subtype": "GENERAL",
      "authorId": "1",
      "authorName": "테스트 Author",
      "priceTier": 2,
      "priceAmount": "2500",
      "priceString": "2,500원",
      "version": 1,
      "versionString": null,
      "validDays": -1,
      "onSale": true,
      "availableForPurchase": true,
      "availableForPresent": true,
      "bargainFlag": false,
      "promotionType": "NONE",
      "stickerResourceType": "ANIMATION",
      "sticonResourceType": null,
      "hasAnimation": false,
      "hasSound": false,
      "payloadsToPreviews": [],
      "sticonPayloadForProduct": null,
      "sticonPayloadsToPreviews": [],
      "subscriptionProduct": false,
      "subscriptionOnlyProduct": false,
      "effectSticker": false
    },
    {
      "id": "-11",
      "title": "테스트 2",
      "description": null,
      "newFlag": false,
      "productUrl": "/stickershop/product/-11/ko",
      "type": "STICKER",
      "subtype": "GENERAL",
      "authorId": "1",
      "authorName": "테스트 Author",
      "priceTier": 2,
      "priceAmount": "2500",
      "priceString": "2,500원",
      "version": 6,
      "versionString": null,
      "validDays": -1,
      "onSale": true,
      "availableForPurchase": true,
      "availableForPresent": true,
      "bargainFlag": false,
      "promotionType": "NONE",
      "stickerResourceType": "ANIMATION",
      "sticonResourceType": null,
      "hasAnimation": false,
      "hasSound": false,
      "payloadsToPreviews": [],
      "sticonPayloadForProduct": null,
      "sticonPayloadsToPreviews": [],
      "subscriptionProduct": false,
      "subscriptionOnlyProduct": false,
      "effectSticker": false
    }
  ]
}
"""
)


@pytest.mark.asyncio
async def test_search_with_valid_keyword(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200, json=LINE_MOCKED_BODY)

    result = await search_list_route(keyword="코니", page=1, count=2)

    assert result.result.success is True
    assert result.data.counts == 34
    assert type(result.data.items[0].id) is int
    assert result.data.items[1].id == -11
    assert result.data.items[1].title == "테스트 2"


@pytest.mark.asyncio
async def test_example_full_cycle():
    # 1. fetch list with any available keyword
    # it is not mocked by HTTPXMock.
    searched_result = await search_list_route(keyword="코니", page=1, count=2)
    assert searched_result.result.success is True
    assert searched_result.data.counts != 0
    assert len(searched_result.data.items) != 0
    assert searched_result.data.items[0].id is not None

    # 2. check result is not empty and fetch detail info
    item = searched_result.data.items[0]
    detail_result = await fetch_info_route(item.id)
    assert detail_result.result.success is True
    assert detail_result.data.item_id == item.id
    assert detail_result.data.title == item.title
