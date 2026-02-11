
import asyncio
from sqlalchemy import select, distinct
from database import AsyncSessionLocal
from models import CVAF

async def check_scores():
    async with AsyncSessionLocal() as session:
        print("Checking CVAF Scores...")
        
        # Unique Inspection Scores
        result = await session.execute(select(distinct(CVAF.inspection_score)))
        unique_inspections = result.scalars().all()
        print(f"Unique Inspection Scores: {unique_inspections}")

        # Unique SOS Scores
        result = await session.execute(select(distinct(CVAF.sos_score)))
        unique_sos = result.scalars().all()
        print(f"Unique SOS Scores: {unique_sos}")

        # Inspection Rate Status
        from models import Machine
        result = await session.execute(select(distinct(Machine.psi_status)))
        unique_psi = result.scalars().all()
        print(f"Unique PSI Statuses: {unique_psi}")

if __name__ == "__main__":
    asyncio.run(check_scores())
