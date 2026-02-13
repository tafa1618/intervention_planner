import asyncio
from database import AsyncSessionLocal
from models import User
from routers.auth import get_password_hash
from sqlalchemy import select

async def create_initial_admin():
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(select(User).where(User.email == "admin@neemba.com"))
        user = result.scalar_one_or_none()
        
        if user:
            print("Admin user already exists.")
            return

        print("Creating admin user...")
        admin_user = User(
            email="admin@neemba.com",
            full_name="Super Admin",
            password_hash=get_password_hash("admin123"), # Default password
            role="admin",
            is_active=1
        )
        db.add(admin_user)
        await db.commit()
        print("Admin user created successfully.")
        print("Email: admin@neemba.com")
        print("Password: admin123")

if __name__ == "__main__":
    asyncio.run(create_initial_admin())
