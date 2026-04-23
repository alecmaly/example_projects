"""FastAPI + Pydantic + SQLAlchemy idioms: decorator-based routing,
path/query/body params, dependency injection via Depends, Pydantic
BaseModel, SQLAlchemy declarative model, async endpoint.

Imports mirror real-world shapes; they are not expected to resolve for
static-analysis-only tests.
"""
from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime


app = FastAPI(title="mono-web")


# --- SQLAlchemy declarative model ---
class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String(128), unique=True, nullable=False)
    name: Optional[str] = Column(String(128), nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)


# --- Pydantic request/response models ---
class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(default=None, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str]

    class Config:
        from_attributes = True


# --- dependency: DB session ---
engine = create_async_engine("sqlite+aiosqlite:///./app.db")
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


# --- dependency: auth ---
async def current_user_id(authorization: Annotated[str, Query()] = "") -> int:
    if not authorization:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing auth")
    return 1


# --- routes ---
@app.get("/users/{user_id}", response_model=UserOut, status_code=200)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserOut:
    result = await db.execute(select(UserRow).where(UserRow.id == user_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    return UserOut.model_validate(row)


@app.get("/users", response_model=list[UserOut])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
) -> list[UserOut]:
    stmt = select(UserRow)
    if search:
        stmt = stmt.where(UserRow.email.like(f"%{search}%"))
    stmt = stmt.limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    return [UserOut.model_validate(r) for r in rows]


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    req: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    creator: Annotated[int, Depends(current_user_id)],
) -> UserOut:
    row = UserRow(email=req.email, name=req.name)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    print(f"creator={creator} new={row.email}")
    return UserOut.model_validate(row)


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
