from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationView
from app.services.investment import investment_process

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Получение списка всех пожертвований - только для суперюзеров."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=List[DonationView],
    response_model_exclude_none=True
)
async def get_user_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение списка всех пожертвований текущего пользователя."""
    return await donation_crud.get_user_donations(user, session)


@router.post(
    '/',
    response_model=DonationView,
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Создание пожертвования - для аутентифицированного пользователя."""
    donation = await donation_crud.create(donation, session, user)
    donation = await investment_process(session, donation)
    return donation
