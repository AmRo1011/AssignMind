import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = "postgresql+asyncpg://postgres.jdsmikadmwavhygcchqf:AssignMind2026Db@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
engine = create_async_engine(DATABASE_URL)

async def check():
    async with engine.connect() as conn:
        from sqlalchemy import text
        result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users'"))
        columns = [row[0] for row in result.fetchall()]
        print("COLUMNS:")
        print(columns)
        print("Is otp_code there?", "otp_code" in columns)

if __name__ == '__main__':
    asyncio.run(check())
