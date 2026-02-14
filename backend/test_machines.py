
import asyncio
import httpx

API_URL = "http://localhost:8000"

async def test_machines():
    async with httpx.AsyncClient() as client:
        print("Fetching Machines...")
        response = await client.get(f"{API_URL}/machines/?limit=5")
        print(f"Fetch Response: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to fetch machines:", response.text)
            return

        machines = response.json()
        print(f"Fetched {len(machines)} machines.")
        
        if machines:
            print("Example Machine:", machines[0])

if __name__ == "__main__":
    asyncio.run(test_machines())
