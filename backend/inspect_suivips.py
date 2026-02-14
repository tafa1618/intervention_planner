
import asyncio
from sqlalchemy import select
from database import AsyncSessionLocal
from models import SuiviPS

async def inspect():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(SuiviPS).limit(5))
        rows = result.scalars().all()
        for row in rows:
            print(f"ID: {row.id}, Serial: {row.serial_number}, Status: {row.status}, Type: {row.ps_type}, Desc: {row.description}, Deadline: {row.deadline}, Action: {row.action_required}")

if __name__ == "__main__":
    asyncio.run(inspect())
