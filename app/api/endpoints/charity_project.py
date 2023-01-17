from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_amount, check_closed, check_existence,
                                check_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charityproject_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment import investment_process

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_charityproject(
    charityproject: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Создание проекта - только для суперюзеров."""
    await check_name_duplicate(charityproject.name, session)
    new_project = await charityproject_crud.create(charityproject, session)
    new_project = await investment_process(session, new_project)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_charityprojects(
    session: AsyncSession = Depends(get_async_session)
):
    """Получение списка всех благотворительных проектов."""
    return await charityproject_crud.get_multi(session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charityproject(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Удаление проекта - только для суперюзеров."""
    project = await check_existence(project_id, session)
    project = check_amount(project)
    project = await charityproject_crud.remove(project, session)
    return project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def partially_update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Редактирование проекта - только для суперюзеров."""
    project = await check_existence(project_id, session)
    check_closed(project)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        check_amount(project, obj_in.full_amount)
    project = await charityproject_crud.update(obj_in, project, session)
    return project
