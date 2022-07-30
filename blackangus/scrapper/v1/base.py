import abc
from typing import TypeVar, Generic, Union, Dict

from httpx import AsyncClient

# 데이터 모델의 제네릭 타입 변수
T = TypeVar("T")


class BaseScrapper(Generic[T], metaclass=abc.ABCMeta):
    httpx: AsyncClient

    def __init__(self):
        self.httpx = AsyncClient()

    async def finalize(self):
        await self.httpx.aclose()

    @abc.abstractmethod
    async def scrape(self, arguments: Dict[str, Union[str, int]]) -> T:
        pass
