from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charityproject_crud
from app.models import CharityProject

NAME_DUPLICATE = 'Проект с таким именем уже существует!'
PROJECT_CLOSE = 'Закрытый проект нельзя редактировать!'
PROJECT_RAISING_MONEY = 'В проект были внесены средства, не подлежит удалению!'
SUMM_LOWER = 'Нельзя установить сумму меньше уже вложенной: '
PROJECT_NOT_FOUND = 'Не найден благотворительный проект по id: '


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession
) -> None:
    """Проверка уникальности имени проекта."""
    project = await charityproject_crud.get_project_id_by_name(
        project_name, session
    )
    if project:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NAME_DUPLICATE
        )


async def check_existence(
    project_id: int,
    session: AsyncSession
) -> CharityProject:
    """Проверка существования проекта в базе данных."""
    project = await charityproject_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECT_NOT_FOUND + f'{project_id}'
        )
    return project


def check_amount(obj, new_amount=None):
    """Проверка вложенных средств при update и delete."""
    invested = obj.invested_amount
    if new_amount:
        if invested > new_amount:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=SUMM_LOWER + f'{invested}'
            )
    elif invested > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_RAISING_MONEY
        )
    return obj


def check_closed(obj):
    """Проверка - если проект закрыт, редактирование запрещено."""
    if obj.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_CLOSE
        )
