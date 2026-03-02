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

# 测试获取收藏项目
def test_get_favorites():
    token = get_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 测试获取收藏项目
    response = requests.get(f"{BASE_URL}/projects/favorites", headers=headers)
    print("\n=== Testing get_favorites ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# 测试切换收藏状态
def test_toggle_favorite(project_id):
    token = get_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 测试切换收藏状态
    response = requests.post(f"{BASE_URL}/projects/{project_id}/favorite", headers=headers)
    print(f"\n=== Testing toggle_favorite for project {project_id} ===")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    # 测试获取收藏项目
    test_get_favorites()
    
    # 测试切换收藏状态（假设项目ID为1）
    test_toggle_favorite(1)
    # 再次测试获取收藏项目
    test_get_favorites()
    
    # 再次切换收藏状态（取消收藏）
    test_toggle_favorite(1)
    # 再次测试获取收藏项目
    test_get_favorites()
