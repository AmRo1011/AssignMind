import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.twilio_service import send_otp
from app.models.user import User
import uuid

async def main():
    async with AsyncSessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            supabase_id=uuid.uuid4(),
            email='test2@test.com',
            full_name='test'
        )
        db.add(user)
        try:
            await send_otp(db, user, '+123456')
        except Exception as e:
            print("ERROR", str(e))
            raise e
        print("Done")

if __name__ == '__main__':
    asyncio.run(main())
