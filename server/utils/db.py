import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from passlib.context import CryptContext
from server.models.user import Base, User

# 优先用环境变量 DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # 如果没有，则用默认模板，并从环境变量取密码
    password = os.getenv("POSTGRES_PASSWORD", "")
    DATABASE_URL = f"postgresql+asyncpg://postgres:{password}@db:5432/stock_scanner"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'user'
    # ...

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 检查是否已有用户，没有则插入默认用户
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == 'cocodady'))
        user = result.scalar_one_or_none()
        if not user:
            from os import getenv
            password = getenv("LOGIN_PASSWORD")
            hashed = pwd_context.hash(password)
            session.add(User(username='cocodady', hashed_password=hashed))
            await session.commit()
