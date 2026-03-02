import requests
import json

# 测试服务器地址
BASE_URL = "http://localhost:8000/api/v1"

# 测试用户凭据
TEST_EMAIL = "admin@3dai.com"
TEST_PASSWORD = "admin123456"

# 获取JWT token
def get_token():
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Failed to get token:", response.json())
        return None

# 测试获取公共项目列表
def test_get_public_projects():
    token = get_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 测试获取公共项目列表
    response = requests.get(f"{BASE_URL}/projects/public/list", headers=headers)
    print("\n=== Testing get_public_projects ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    # 测试获取公共项目列表
    test_get_public_projects()
