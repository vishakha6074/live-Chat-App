from fastapi import APIRouter, HTTPException
from database.db import SessionLocal
from models.user import User
from auth.utils import hash_password, verify_password, create_token
from sqlalchemy.future import select

router = APIRouter()

@router.post("/signup")
async def signup(username: str, password: str):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        if result.scalar():
            raise HTTPException(status_code=400, detail="User exists")

        user = User(username=username, password=hash_password(password))
        session.add(user)
        await session.commit()

        return {"msg": "User created"}

@router.post("/login")
async def login(username: str, password: str):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar()

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token({"sub": username})
        return {"access_token": token}