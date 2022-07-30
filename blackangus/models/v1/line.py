from typing import List, Optional

from pydantic import BaseModel


class LineconCategoryModel(BaseModel):
    title: str
    id: int
    link: str


class LineconItemModel(BaseModel):
    type: str
    item_id: str
    url: str
    sound_url: Optional[str]


class LineconCategoryDetailModel(BaseModel):
    item_id: int
    title: str
    description: str
    author: str
    items: List[LineconItemModel]


class LineconCategoriesWithCountModel(BaseModel):
    counts: int
    items: List[LineconCategoryModel]
