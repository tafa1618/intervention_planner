
import asyncio
import httpx

API_URL = "http://localhost:8000"

async def test_interventions():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Generate Interventions
        print("Generating Interventions...")
        response = await client.post(f"{API_URL}/interventions/generate")
        print(f"Generate Response: {response.status_code} - {response.text}")
        
        if response.status_code != 200:
            print("Failed to generate interventions.")
            return

        generate_data = response.json()
        count = generate_data.get("count", 0)
        print(f"Generated {count} interventions.")

        # 2. Fetch Interventions
        print("Fetching Interventions...")
        response = await client.get(f"{API_URL}/interventions/")
        print(f"Fetch Response: {response.status_code}")
        
        interventions = response.json()
        print(f"Fetched {len(interventions)} interventions.")
        
        # 3. Analyze Types & Priorities
        types = {}
        priorities = {}
        for i in interventions:
            t = i['type']
            p = i['priority']
            types[t] = types.get(t, 0) + 1
            priorities[p] = priorities.get(p, 0) + 1
            
        print("Intervention Types:", types)
        print("Intervention Priorities:", priorities)
        
        # 4. Check Examples
        if interventions:
            print("Example Intervention:", interventions[0])

if __name__ == "__main__":
    asyncio.run(test_interventions())
