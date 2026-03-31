import asyncio
from sqlalchemy import select

from core.database import AsyncSessionLocal
from domain.models.user import User

async def view_users():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print(" No users found in database")
                return
            
            print("=" * 80)
            print("USERS TABLE")
            print("=" * 80)
            
            for user in users:
                print(f"\nID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Password Hash: {user.password_hash[:50]}...")
                print(f"Must Change Password: {user.must_change_password}")
                print(f"Password Changed At: {user.password_changed_at}")
                print(f"Created At: {user.created_at}")
                print(f"Updated At: {user.updated_at}")
                print("-" * 80)
                
        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    asyncio.run(view_users())