from typing import Generic, TypeVar

from pydantic import BaseModel


class APIResultModel(BaseModel):
    success: bool
    message: str


class BaseResponse(BaseModel):
    result: APIResultModel


T = TypeVar("T")


class ValuedResponse(BaseResponse, Generic[T]):
    data: T


SUCCESS_DEFAULT_RESPONSE = APIResultModel(
    success=True,
    message="Success",
)
