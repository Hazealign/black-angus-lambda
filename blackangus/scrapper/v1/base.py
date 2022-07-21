import abc
import os
from typing import TypeVar, Generic, Optional, List, Union, Dict

from playwright.async_api import async_playwright, Playwright, Browser, Page
from playwright_stealth import stealth_async as stealth

# 데이터 모델의 제네릭 타입 변수
T = TypeVar("T")


class ScrapperException(BaseException):
    pass


class BaseScrapper(Generic[T], metaclass=abc.ABCMeta):
    playwright_instance: Optional[Playwright] = None
    browser: Optional[Browser] = None

    def __init__(self):
        self.playwright_manager = async_playwright()

    async def initialize(self):
        if self.playwright_instance is None:
            self.playwright_instance = await self.playwright_manager.start()

        if self.browser is None:
            executable_path = (
                self.playwright_instance.chromium.executable_path
                if os.environ.get("IS_AWS_LAMBDA", None) is None
                else "/var/task/bin/headless-chromium"
            )

            self.browser = await self.playwright_instance.chromium.launch(
                headless=True,
                executable_path=executable_path,
                args=[
                    "--headless",
                    "--disable-gpu",
                    "--single-process",
                    "--no-sandbox",
                    "--window-size=1920,1200",
                    "--disable-extensions",
                    "--incognito",
                    "--v=99",
                    "--no-zygote",
                    "--deterministic-fetch",
                    "--disable-dev-shm-usage",
                ],
            )

    # 페이지를 만들 때는 스텔싱을 위해 이걸 쓴다.
    async def create_page(self) -> Page:
        if self.browser is None or self.playwright_instance is None:
            raise ScrapperException("아직 Initialize 되지 않은 인스턴스입니다.")

        page = await self.browser.new_page()
        await stealth(page)
        return page

    async def finalize(self):
        if self.browser is None or self.playwright_instance is None:
            raise ScrapperException("아직 Initialize 되지 않은 인스턴스입니다.")

        await self.browser.close()
        await self.playwright_instance.stop()
        await self.playwright_manager.__aexit__()

    @abc.abstractmethod
    async def scrape(self, arguments: Dict[str, Union[str, int]]) -> Union[T, List[T]]:
        pass
