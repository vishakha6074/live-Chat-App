from fastapi import APIRouter
from sqlalchemy.future import select
from database.db import SessionLocal
from models.message import MessageDB

router = APIRouter()

@router.get("/messages")
async def get_messages():
    async with SessionLocal() as session:
        result = await session.execute(select(MessageDB))
        messages = result.scalars().all()

        return messages