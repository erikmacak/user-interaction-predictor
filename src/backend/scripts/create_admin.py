import asyncio
from sqlalchemy import select

from core.database import AsyncSessionLocal
from core.settings import settings
from core.security import get_password_hash
from domain.models.user import User

async def create_admin_user():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User).where(User.username == "admin")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(" Admin user already exists!")
                print(f"   Username: {existing_user.username}")
                print(f"   Created: {existing_user.created_at}")
                return
            
            admin = User(
                username="admin",
                password_hash=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                must_change_password=True, 
            )
            
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            
            print(" Admin user created successfully!")
            print("=" * 50)
            print(f"   Username: {admin.username}")
            print(f"   Password: {settings.INITIAL_ADMIN_PASSWORD}")
            print("=" * 50)
            print("  CHANGE PASSWORD AFTER FIRST LOGIN!")
            print("=" * 50)
            
        except Exception as e:
            await db.rollback()
            print(f" Error creating admin user: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(create_admin_user())