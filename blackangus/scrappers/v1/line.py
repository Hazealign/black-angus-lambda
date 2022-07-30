from typing import List

import lxml.html
import ujson
from fastapi import HTTPException

from blackangus.models.v1.line import LineconCategoryDetailModel, LineconItemModel
from .base import BaseScrapper

FAKE_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/103.0.0.0 Safari/537.36"
)


class LineScrapperException(Exception):
    pass


class LineEmoticonScrapper(BaseScrapper[int, LineconCategoryDetailModel]):
    async def scrap(
        self,
        value: int,
    ) -> LineconCategoryDetailModel:
        response = await self.httpx.get(
            f"https://store.line.me/stickershop/product/{value}/ko",
            timeout=None,
            headers={
                "User-Agent": FAKE_USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
                "Accept-Language": "ko-KR,ko;q=0.9",
            },
        )

        if not response.is_success:
            raise HTTPException(
                status_code=response.status_code,
                detail="Server returned invalid status code.",
            )

        root_element = lxml.html.fromstring(response.text)

        title_candidates = root_element.cssselect("p.mdCMN38Item01Ttl")
        if title_candidates is None or len(title_candidates) == 0:
            raise LineScrapperException(
                f"Can't find any result from Line Sticker ID: {value}"
            )
        title: str = title_candidates[0].text_content()

        description_candidates = root_element.cssselect("p.mdCMN38Item01Txt")
        if description_candidates is None or len(description_candidates) == 0:
            raise LineScrapperException(
                f"Can't find any result from Line Sticker ID: {value}"
            )
        description: str = description_candidates[0].text_content()

        author_candidates = root_element.cssselect("a.mdCMN38Item01Author")
        if author_candidates is None or len(author_candidates) == 0:
            raise LineScrapperException(
                f"Can't find any result from Line Sticker ID: {value}"
            )
        author: str = author_candidates[0].text_content()

        items: List[LineconItemModel] = []
        item_candidates = root_element.cssselect("li.mdCMN09Li.FnStickerPreviewItem")
        for candidate in item_candidates:
            data_string = candidate.attrib.get("data-preview", None)
            if data_string is None:
                continue

            # we don't use orjson cause of in lambda environment,
            # it's difficult to provide to build with Rust.
            data = ujson.loads(data_string)

            item_id = data["id"]
            item_type = data["type"]
            item_url = (
                data["animationUrl"] if "animation" == item_type else data["staticUrl"]
            )
            item_sound_url = None if data["soundUrl"] == "" else data["soundUrl"]

            items.append(
                LineconItemModel(
                    item_id=item_id,
                    type=item_type,
                    url=item_url,
                    sound_url=item_sound_url,
                )
            )

        return LineconCategoryDetailModel(
            item_id=value,
            title=title,
            description=description,
            author=author,
            items=items,
        )
