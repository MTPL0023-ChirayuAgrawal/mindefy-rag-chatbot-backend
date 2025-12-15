from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from db.mongo import get_database


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# Request Schemas
class MessageCreate(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatCreateRequest(BaseModel):
    user_input: str


class ChatUpdateRequest(BaseModel):
    title: str


# Response Schemas
class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatHistoryListItem(BaseModel):
    id: str = Field(alias="_id")
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        populate_by_name = True


class ChatHistoryDetail(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class ChatResponse(BaseModel):
    chat_id: str
    response: str
    title: str


class DeleteResponse(BaseModel):
    success: bool
    message: str