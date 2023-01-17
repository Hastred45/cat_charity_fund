from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def check_not_invested(
    session: AsyncSession,
):
    """Получение из БД первых по очереди незакрытых проектов и пожертвований."""
    project = await session.execute(select(CharityProject).where(
        CharityProject.fully_invested == 0
    ).order_by('create_date'))
    project = project.scalars().first()
    donation = await session.execute(select(Donation).where(
        Donation.fully_invested == 0
    ).order_by('create_date'))
    donation = donation.scalars().first()
    return project, donation


async def investment_process(
    session: AsyncSession,
    obj
):
    """Инвестирование пожертвований в незакрытые проекты."""
    project, donation = await check_not_invested(session)
    if not project or not donation:
        await session.commit()
        await session.refresh(obj)
        return obj
    balance_project = project.full_amount - project.invested_amount
    balance_donation = donation.full_amount - donation.invested_amount
    if balance_project > balance_donation:
        project.invested_amount += balance_donation
        donation.invested_amount += balance_donation
        donation.fully_invested = True
        donation.close_date = datetime.now()
    elif balance_project == balance_donation:
        project.invested_amount += balance_donation
        donation.invested_amount += balance_donation
        project.fully_invested = True
        donation.fully_invested = True
        project.close_date = datetime.now()
        donation.close_date = datetime.now()
    else:
        project.invested_amount += balance_project
        donation.invested_amount += balance_project
        project.fully_invested = True
        project.close_date = datetime.now()
    session.add(project)
    session.add(donation)
    await session.commit()
    await session.refresh(project)
    await session.refresh(donation)
    return await investment_process(session, obj)
