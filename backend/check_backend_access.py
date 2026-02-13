import urllib.request
import time
import json

def check_backend():
    base_url = "http://localhost:8000"
    print(f"Checking {base_url}...")
    
    try:
        start = time.time()
        with urllib.request.urlopen(f"{base_url}/docs", timeout=5) as r:
            print(f"GET /docs: Status {r.status} in {time.time() - start:.2f}s")
    except Exception as e:
        print(f"GET /docs failed: {e}")

    try:
        print(f"Checking {base_url}/machines/ ...")
        start = time.time()
        with urllib.request.urlopen(f"{base_url}/machines/", timeout=10) as r:
            data = json.loads(r.read().decode())
            print(f"GET /machines/: Status {r.status} in {time.time() - start:.2f}s")
            print(f"Returned {len(data)} machines.")
    except Exception as e:
        print(f"GET /machines/ failed: {e}")

if __name__ == "__main__":
    check_backend()
