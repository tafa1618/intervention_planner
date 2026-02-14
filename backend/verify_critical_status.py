
import asyncio
import httpx
from sqlalchemy import select
from database import AsyncSessionLocal
from models import Intervention, Machine

API_URL = "http://localhost:8000"

async def verify_critical():
    # 1. Find a machine Serial with pending HIGH priority intervention
    async with AsyncSessionLocal() as session:
        stmt = select(Machine.serial_number).join(Intervention).where(
            Intervention.status == 'PENDING',
            Intervention.priority == 'HIGH'
        ).limit(1)
        result = await session.execute(stmt)
        serial_number = result.scalar()
        
        if not serial_number:
            print("No machines found with PENDING HIGH priority intervention in DB.")
            return

        print(f"Found machine Serial {serial_number} with HIGH priority intervention.")
        
        # 2. Call API with filter
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/machines/?serialNumber={serial_number}")
            if response.status_code != 200:
                print(f"Failed to fetch machine: {response.status_code}")
                return
            
            machines = response.json()
            if not machines:
                print("API returned no machines for this serial.")
                return

            machine = machines[0]
            print(f"API Returned Matching Machine: {machine['serialNumber']}")
            print(f"Status: {machine['status']}")
            
            if machine['status'] == 'critical':
                print("SUCCESS: Machine status is 'critical'.")
            else:
                print(f"FAILURE: Machine status is '{machine['status']}', expected 'critical'.")

async def main():
    await verify_critical()

if __name__ == "__main__":
    asyncio.run(main())
