
import asyncio
import httpx

API_URL = "http://localhost:8000"

async def test_desc():
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{API_URL}/interventions/")
        interventions = response.json()
        
        suivi_ps = next((i for i in interventions if i['type'] == 'SUIVI_PS'), None)
        if suivi_ps:
            print("SuiviPS Example:")
            print(f"ID: {suivi_ps['id']}")
            print(f"Description: {suivi_ps['description']}")
        else:
            print("No SuiviPS found.")

if __name__ == "__main__":
    asyncio.run(test_desc())
