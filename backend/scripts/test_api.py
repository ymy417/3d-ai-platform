import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """测试用户注册"""
    print("=" * 50)
    print("测试用户注册")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 201
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_login():
    """测试用户登录"""
    print("\n" + "=" * 50)
    print("测试用户登录")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_get_me(token):
    """测试获取当前用户信息"""
    print("\n" + "=" * 50)
    print("测试获取当前用户信息")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_update_profile(token):
    """测试更新用户信息"""
    print("\n" + "=" * 50)
    print("测试更新用户信息")
    print("=" * 50)
    
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "phone": "13800138000",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    print("开始测试用户认证API...")
    print(f"API地址: {BASE_URL}")
    
    # 测试注册
    if test_register():
        print("✅ 注册测试通过")
    else:
        print("❌ 注册测试失败")
    
    # 测试登录
    token = test_login()
    if token:
        print("✅ 登录测试通过")
        
        # 测试获取用户信息
        if test_get_me(token):
            print("✅ 获取用户信息测试通过")
        else:
            print("❌ 获取用户信息测试失败")
        
        # 测试更新用户信息
        if test_update_profile(token):
            print("✅ 更新用户信息测试通过")
        else:
            print("❌ 更新用户信息测试失败")
    else:
        print("❌ 登录测试失败")
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)
