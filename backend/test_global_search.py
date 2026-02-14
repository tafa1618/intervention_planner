import asyncio
import httpx
import json

API_URL = "http://localhost:8000"

async def test_global_search():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Search for our test client
        query = "Test Client" 
        print(f"Searching for '{query}'...")
        
        response = await client.get(f"{API_URL}/machines/global-search?q={query}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} machines.")
            if data:
                print("Sample Machine Context:")
                print(json.dumps(data[0], indent=2))
        else:
            print("Error response:", response.text)

        # Search for something else to test filtration
        query = "CAT"
        print(f"\nSearching for '{query}'...")
        response = await client.get(f"{API_URL}/machines/global-search?q={query}")
        if response.status_code == 200:
             print(f"Found {len(response.json())} machines.")

if __name__ == "__main__":
    asyncio.run(test_global_search())
