"""
이벤트 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.common import PageRequest, PageResponse


class EventBase(BaseModel):
    """이벤트 기본 스키마"""
    title: str = Field(..., max_length=255, description="이벤트 제목")
    description: Optional[str] = Field(None, description="설명")
    start_at: datetime = Field(..., description="시작 시간")
    end_at: datetime = Field(..., description="종료 시간")
    location: Optional[str] = Field(None, max_length=500, description="장소")
    is_all_day: bool = Field(False, description="종일 이벤트 여부")


class EventCreate(EventBase):
    """이벤트 생성 요청"""
    calendar_id: str = Field(..., description="캘린더 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "calendar_id": "uuid-of-calendar",
                "title": "Team Meeting",
                "description": "Weekly sync meeting",
                "start_at": "2025-12-25T10:00:00Z",
                "end_at": "2025-12-25T11:00:00Z",
                "location": "Conference Room A",
                "is_all_day": False
            }
        }


class EventUpdate(BaseModel):
    """이벤트 수정 요청"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=500)
    is_all_day: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Rescheduled Meeting",
                "start_at": "2025-12-25T14:00:00Z",
                "end_at": "2025-12-25T15:00:00Z"
            }
        }


class EventResponse(EventBase):
    """이벤트 응답"""
    id: str
    calendar_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventListRequest(PageRequest):
    """이벤트 목록 조회 요청"""
    calendar_id: Optional[str] = None
    start_from: Optional[datetime] = None
    start_to: Optional[datetime] = None
    end_from: Optional[datetime] = None
    end_to: Optional[datetime] = None
    is_all_day: Optional[bool] = None


class EventListResponse(PageResponse[EventResponse]):
    """이벤트 목록 응답"""
    pass






