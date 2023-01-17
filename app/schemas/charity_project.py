from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, validator


class CharityProjectUpdate(BaseModel):
    """Схема для обновления проекта."""
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, min_length=1)
    full_amount: int = Field(None, gt=0)

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectUpdate):
    """Схема для создания проекта."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    full_amount: int = Field(..., gt=0)

    @validator('name', 'description')
    def none_and_empty_not_allowed(cls, value: str):
        if not value or value is None:
            raise ValueError('Все поля обязательны. "" или None не допускаются.')
        return value


class CharityProjectDB(CharityProjectCreate):
    """Схема со всеми данными проекта."""
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
