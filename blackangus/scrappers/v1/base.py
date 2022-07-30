import abc
from typing import TypeVar, Generic

from httpx import AsyncClient

# 데이터 모델의 제네릭 타입 변수
Arguments = TypeVar("Arguments")
Response = TypeVar("Response")


class BaseScrapper(Generic[Arguments, Response], metaclass=abc.ABCMeta):
    httpx: AsyncClient

    def __init__(self):
        self.httpx = AsyncClient()

    async def finalize(self):
        await self.httpx.aclose()

    @abc.abstractmethod
    async def scrape(self, value: Arguments) -> Response:
        pass
