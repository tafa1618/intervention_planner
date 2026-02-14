
import asyncio
import httpx

API_URL = "http://localhost:8000"

async def test_search():
    async with httpx.AsyncClient() as client:
        # Test 1: Search by partial serial (e.g., 'CAT') - assuming some serials contain it or just pick a known one
        # Let's first get a known serial to search for
        print("Fetching a machine to use as search target...")
        resp = await client.get(f"{API_URL}/machines/?limit=1")
        if resp.status_code != 200:
            print("Failed to fetch initial machine")
            return
        
        machine = resp.json()[0]
        serial = machine['serialNumber']
        partial_serial = serial[:4]
        
        print(f"Testing search with partial serial: {partial_serial}")
        search_resp = await client.get(f"{API_URL}/machines/?search={partial_serial}")
        
        if search_resp.status_code == 200:
            results = search_resp.json()
            print(f"Found {len(results)} machines matching '{partial_serial}'")
            matched = any(m['serialNumber'] == serial for m in results)
            print(f"Original machine found in results: {matched}")
        else:
            print(f"Search failed: {search_resp.status_code}")

        # Test 2: Search by Client Name
        client_name = machine['client']
        if client_name == "Unknown Client":
            print("Skipping client search test (Unknown Client)")
        else:
            partial_client = client_name[:4]
            print(f"Testing search with partial client: {partial_client}")
            client_search_resp = await client.get(f"{API_URL}/machines/?search={partial_client}")
            if client_search_resp.status_code == 200:
                c_results = client_search_resp.json()
                print(f"Found {len(c_results)} machines for client '{partial_client}'")
                c_matched = any(m['client'] == client_name for m in c_results)
                print(f"Original client found in results: {c_matched}")

if __name__ == "__main__":
    asyncio.run(test_search())
