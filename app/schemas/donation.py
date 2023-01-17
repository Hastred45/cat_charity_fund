from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field


class DonationCreate(BaseModel):
    """Схема для создания пожертвования."""
    full_amount: int = Field(..., gt=0)
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationView(DonationCreate):
    """Схема для отображения в ответе."""
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationView):
    """Схема со всеми данными объекта пожертвования."""
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
