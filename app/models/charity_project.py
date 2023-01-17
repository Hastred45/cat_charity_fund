from sqlalchemy import Column, String, Text

from app.models.abstract_models import AbstractModel


class CharityProject(AbstractModel):
    """Модель для целевых проектов."""
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
