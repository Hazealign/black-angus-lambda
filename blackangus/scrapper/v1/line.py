import orjson
from typing import List, Dict, Union

from blackangus.models.v1.line import LineconCategoryDetailModel, LineconItemModel
from blackangus.scrapper.v1.base import BaseScrapper, ScrapperException


class LineEmoticonScrapper(BaseScrapper[LineconCategoryDetailModel]):
    async def scrape(
        self,
        arguments: Dict[str, Union[str, int]],
    ) -> Union[LineconCategoryDetailModel, List[LineconCategoryDetailModel]]:
        linecon_id = arguments.get("id", None)

        if linecon_id is None or type(linecon_id) is not int:
            raise ScrapperException("지정된 라인 이모티콘 ID가 없습니다.")

        page = await self.create_page()
        await page.goto(
            f"https://line.me/S/sticker/{linecon_id}/?lang=ko&ref=gnsh_stickerDetail",
            wait_until="networkidle",
        )

        title = await page.inner_text("p.mdCMN38Item01Ttl")
        description = await page.inner_text("p.mdCMN38Item01Txt")
        author = await page.inner_text("p.mdCMN38Item01Author")

        items: List[LineconItemModel] = []
        json_strings = await page.evaluate(
            """
            () => Array.from(
                document.querySelectorAll('li.mdCMN09Li.FnStickerPreviewItem')
            ).map(item => item.attributes['data-preview'].value)
        """
        )

        for json_string in json_strings:
            json_value = orjson.loads(json_string)

            item_id = json_value["id"]
            item_type = json_value["type"]
            item_url = (
                json_value["animationUrl"]
                if item_type.__contains__("animation")
                else json_value["staticUrl"]
            )
            item_sound_url = (
                None if json_value["soundUrl"] == "" else json_value["soundUrl"]
            )

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
