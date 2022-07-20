from typing import List
from urllib.parse import quote_plus

import httpx
from flask import request, jsonify

# 대충 적당한 User Agent를 넣어준다.
from blackangus.models.v1.line import LineconCategoryModel, LineconCategoryDetailModel
from blackangus.scrapper.v1.line import LineEmoticonScrapper

FAKE_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/103.0.0.0 Safari/537.36"
)


async def search_list_route():
    keyword = request.args.get("keyword", None)
    page = int(request.args.get("page", "-1"))
    limit = int(request.args.get("limit", "-1"))

    if keyword is None or page == -1 or limit == -1:
        return {
            "result": {
                "success": False,
                "message": "Invalid Request Parameters",
            }
        }, 400

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://store.line.me/api/search/sticker",
            headers={
                "User-Agent": FAKE_USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
                "Referrer": f"https://store.line.me/search/sticker/ko?q={quote_plus(keyword)}",
            },
            params={
                "query": keyword,
                "offset": f"{limit * (page - 1)}",
                "limit": f"{limit}",
                "type": "ALL",
                "includeFacets": "true",
            },
        )

        body = await response.json()

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

        return {
            "result": {
                "success": True,
                "message": "Successfully Fetched",
            },
            "data": {
                "counts": counts,
                "items": jsonify(items),
            },
        }, 200


async def fetch_info_route(linecon_id: int):
    try:
        scrapper = LineEmoticonScrapper()
        await scrapper.initialize()

        result = await scrapper.scrape(
            {
                "id": linecon_id,
            }
        )

        assert result is not None and type(result) is LineconCategoryDetailModel

        return {
            "result": {
                "success": True,
                "message": "Successfully Fetched",
            },
            "data": jsonify(result),
        }
    except Exception as e:
        return {
            "result": {
                "success": False,
                "message": "Failure during scrapping Line Emoticon.",
                "error": str(e),
            }
        }, 500
