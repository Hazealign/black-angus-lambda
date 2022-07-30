from typing import List, Union
from urllib.parse import quote_plus

import httpx
from fastapi import APIRouter, HTTPException

from blackangus.models.v1 import ValuedResponse, SUCCESS_DEFAULT_RESPONSE
from blackangus.models.v1.line import (
    LineconCategoryModel,
    LineconCategoryDetailModel,
    LineconCategoriesWithCountModel,
)
from blackangus.scrapper.v1.line import LineEmoticonScrapper, FAKE_USER_AGENT

router = APIRouter(
    prefix="/api/v1/line",
    tags=["LineEmoticon"],
    responses={
        404: (
            {
                "result": {
                    "success": False,
                    "message": "Not Found",
                }
            }
        ),
        400: ({"result": {"success": False, "message": "Invalid Request Parameters"}}),
    },
)


@router.get("/list", response_model=ValuedResponse[LineconCategoriesWithCountModel])
async def search_list_route(
    keyword: Union[str, None] = None,
    page: int = 1,
    limit: int = 10,
) -> ValuedResponse[LineconCategoriesWithCountModel]:
    if keyword is None:
        raise HTTPException(status_code=400, detail="keyword value must be not None.")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://store.line.me/api/search/sticker",
            headers={
                "User-Agent": FAKE_USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
                "Referrer": f"https://store.line.me/search/sticker/ko?q={quote_plus(keyword)}",
                "Accept-Language": "ko-KR,ko;q=0.9",
            },
            params={
                "query": keyword,
                "offset": f"{limit * (page - 1)}",
                "limit": f"{limit}",
                "type": "ALL",
                "includeFacets": "true",
            },
        )

        body = response.json()

    counts = body.get("totalCount", 0)
    primitive_items = body.get("items", [])
    items: List[LineconCategoryModel] = []

    for item in primitive_items:
        items.append(
            LineconCategoryModel(
                title=item["title"],
                id=int(item["id"]),
                link=f'https://store.line.me/stickershop/product/{item["id"]}/ko',
            )
        )

    return ValuedResponse(
        result=SUCCESS_DEFAULT_RESPONSE,
        data=LineconCategoriesWithCountModel(
            counts=counts,
            items=items,
        ),
    )


@router.get("/{item_id}", response_model=ValuedResponse[LineconCategoryDetailModel])
async def fetch_info_route(item_id: int) -> ValuedResponse[LineconCategoryDetailModel]:
    scrapper = LineEmoticonScrapper()
    result = await scrapper.scrape(
        {
            "id": item_id,
        }
    )

    return ValuedResponse(
        result=SUCCESS_DEFAULT_RESPONSE,
        data=result,
    )
