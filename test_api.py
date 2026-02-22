import requests
import json

try:
    response = requests.get("http://127.0.0.1:8000/jobs/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Count: {len(data)}")
    if data:
        print(f"First job: {json.dumps(data[0], indent=2)}")
except Exception as e:
    print(f"Error: {e}")
