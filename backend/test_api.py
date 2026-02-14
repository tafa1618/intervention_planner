
import urllib.request
import urllib.parse
import os
import mimetypes
import uuid

url = "http://backend:8000/upload-programmes"
file_path = "data/Programmes.xlsx"

if not os.path.exists(file_path):
    if os.path.exists("../data/Programmes.xlsx"):
        file_path = "../data/Programmes.xlsx"
    else:
        print("File not found")
        exit(1)

boundary = uuid.uuid4().hex
headers = {
    "Content-Type": f"multipart/form-data; boundary={boundary}",
}

with open(file_path, "rb") as f:
    file_content = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="Programmes.xlsx"\r\n'
    f"Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n"
).encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")

req = urllib.request.Request(url, data=body, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.status)
        print("Response:", response.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
