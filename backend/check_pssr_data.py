
import asyncio
from sqlalchemy import select, func
from database import AsyncSessionLocal
from models import Client, Machine

async def check_pssr_data():
    async with AsyncSessionLocal() as session:
        print("Checking PSSR data...")
        
        # Check total machines
        result = await session.execute(select(func.count(Machine.id)))
        total_machines = result.scalar()
        print(f"Total Machines in DB: {total_machines}")

        # Check Clients with PSSR
        result = await session.execute(select(func.count(Client.id)).where(Client.pssr.isnot(None)))
        count_clients_with_pssr = result.scalar()
        print(f"Clients with PSSR: {count_clients_with_pssr}")
        
        # Check Machines with last_visit (from Inspection Rate)
        result = await session.execute(select(func.count(Machine.id)).where(Machine.last_visit.isnot(None)))
        count_machines_with_visit = result.scalar()
        print(f"Machines with last_visit: {count_machines_with_visit}")
        
        # Check Machines with psi_status (filled by is_inspected)
        result = await session.execute(select(func.count(Machine.id)).where(Machine.psi_status.isnot(None)))
        count_machines_status = result.scalar()
        print(f"Machines with psi_status: {count_machines_status}")

        # Sample data
        if count_clients_with_pssr > 0:
            result = await session.execute(select(Client.name, Client.pssr).where(Client.pssr.isnot(None)).limit(3))
            print("Sample Clients with PSSR:", result.all())

        if count_machines_with_visit > 0:
            result = await session.execute(select(Machine.serial_number, Machine.last_visit, Machine.psi_status).where(Machine.last_visit.isnot(None)).limit(3))
            print("Sample Machines with Visit Info:", result.all())

if __name__ == "__main__":
    try:
        asyncio.run(check_pssr_data())
    except Exception as e:
        print(f"Error: {e}")
