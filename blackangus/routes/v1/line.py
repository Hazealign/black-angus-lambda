import traceback
from typing import List
from urllib.parse import quote_plus

import httpx
from flask import request, jsonify

# 대충 적당한 User Agent를 넣어준다.
from blackangus.models.v1.line import LineconCategoryModel, LineconCategoryDetailModel
from blackangus.scrapper.v1.line import LineEmoticonScrapper, FAKE_USER_AGENT


async def search_list_route():
    keyword = request.args.get("keyword", None)
    page = int(request.args.get("page", "1"))
    limit = int(request.args.get("limit", "10"))

    if keyword is None:
        return (
            jsonify(
                {
                    "result": {
                        "success": False,
                        "message": "Invalid Request Parameters",
                    }
                }
            ),
            400,
        )

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

        return (
            jsonify(
                {
                    "result": {
                        "success": True,
                        "message": "Successfully Fetched",
                    },
                    "data": {
                        "counts": counts,
                        "items": items,
                    },
                }
            ),
            200,
        )


async def fetch_info_route(linecon_id: int):
    try:
        scrapper = LineEmoticonScrapper()
        result = await scrapper.scrape(
            {
                "id": linecon_id,
            }
        )

        assert result is not None and type(result) is LineconCategoryDetailModel

        return jsonify(
            {
                "result": {
                    "success": True,
                    "message": "Successfully Fetched",
                },
                "data": result,
            }
        )
    except Exception as e:
        traceback.print_exc()
        return (
            jsonify(
                {
                    "result": {
                        "success": False,
                        "message": "Failure during scrapping Line Emoticon.",
                        "error": str(e),
                    }
                }
            ),
            500,
        )
