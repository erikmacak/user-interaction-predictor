import asyncio
from sqlalchemy import select

from core.database import AsyncSessionLocal
from core.settings import settings
from core.security import get_password_hash
from domain.models.user import User

async def reset_admin_password():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User).where(User.username == "admin")
            )
            admin = result.scalar_one_or_none()
            
            if not admin:
                print(" Admin user not found!")
                print("   Run: python -m scripts.create_admin")
                return
            
            admin.password_hash = get_password_hash(settings.INITIAL_ADMIN_PASSWORD)
            admin.must_change_password = True
            admin.password_changed_at = None
            
            db.add(admin)
            await db.commit()
            
            print(" Admin password reset successfully!")
            print("=" * 50)
            print(f"   Username: {admin.username}")
            print(f"   Password: {settings.INITIAL_ADMIN_PASSWORD}")
            print("=" * 50)
            print("  CHANGE PASSWORD AFTER LOGIN!")
            
        except Exception as e:
            await db.rollback()
            print(f" Error resetting password: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(reset_admin_password())