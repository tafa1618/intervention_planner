
import asyncio
from database import AsyncSessionLocal
from models import CVAF
from sqlalchemy import select

async def inspect_scores():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CVAF).limit(20))
        cvafs = result.scalars().all()
        for c in cvafs:
            print(f"Serial: {c.serial_number} | SOS: '{c.sos_score}' | Insp: '{c.inspection_score}'")

if __name__ == "__main__":
    asyncio.run(inspect_scores())
