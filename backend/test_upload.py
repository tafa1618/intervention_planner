import requests

def test_upload():
    url = "http://localhost:8001/admin/upload"
    # Ensure a dummy excel file exists or use an existing one
    file_path = "data/Programmes.xlsx" 
    
    # We need a token. Let's assume we can get one or we disabled auth for test?
    # Auth is enabled. We need to login first.
    
    login_url = "http://localhost:8001/auth/token"
    # You might need to adjust these credentials to a valid admin user in your DB
    admin_creds = {"username": "admin@neemba.com", "password": "adminpassword"} 
    
    session = requests.Session()
    
    try:
        print(f"Logging in as {admin_creds['username']}...")
        resp = session.post(login_url, data=admin_creds)
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
            
        token = resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("Login successful.")

        print(f"Uploading {file_path}...")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            resp = session.post(url, headers=headers, files=files)
            
        if resp.status_code == 200:
            print("Upload Success:", resp.json())
        else:
            print(f"Upload Failed: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_upload()
