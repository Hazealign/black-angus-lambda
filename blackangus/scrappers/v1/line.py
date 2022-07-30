from typing import List, Dict, Union

import lxml.html
import orjson

from blackangus.models.v1.line import LineconCategoryDetailModel, LineconItemModel
from blackangus.scrappers.v1.base import BaseScrapper

FAKE_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/103.0.0.0 Safari/537.36"
)


class LineScrapperException(Exception):
    pass


class LineEmoticonScrapper(BaseScrapper[LineconCategoryDetailModel]):
    async def scrape(
        self,
        arguments: Dict[str, Union[str, int]],
    ) -> LineconCategoryDetailModel:
        linecon_id = arguments.get("id", None)

        if linecon_id is None or type(linecon_id) is not int:
            raise LineScrapperException("지정된 라인 이모티콘 ID가 없습니다.")

        response = await self.httpx.get(
            f"https://store.line.me/stickershop/product/{linecon_id}/ko",
            timeout=None,
            headers={
                "User-Agent": FAKE_USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
                "Accept-Language": "ko-KR,ko;q=0.9",
            },
        )

        root_element = lxml.html.fromstring(response.content)

        title_candidates = root_element.cssselect("p.mdCMN38Item01Ttl")
        if title_candidates is None or len(title_candidates) == 0:
            raise LineScrapperException("라인 이모티콘 ID로 나온 결과가 없습니다.")
        title: str = title_candidates[0].text_content()

        description_candidates = root_element.cssselect("p.mdCMN38Item01Txt")
        if description_candidates is None or len(description_candidates) == 0:
            raise LineScrapperException("라인 이모티콘 ID로 나온 결과가 없습니다.")
        description: str = description_candidates[0].text_content()

        author_candidates = root_element.cssselect("a.mdCMN38Item01Author")
        if author_candidates is None or len(author_candidates) == 0:
            raise LineScrapperException("라인 이모티콘 ID로 나온 결과가 없습니다.")
        author: str = author_candidates[0].text_content()

        items: List[LineconItemModel] = []
        item_candidates = root_element.cssselect("li.mdCMN09Li.FnStickerPreviewItem")
        for candidate in item_candidates:
            data_string = candidate.attrib.get("data-preview", None)
            if data_string is None:
                continue

            data = orjson.loads(data_string)

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
            item_id=linecon_id,
            title=title,
            description=description,
            author=author,
            items=items,
        )
