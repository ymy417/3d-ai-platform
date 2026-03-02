import requests

# 测试画廊API
def test_gallery_api():
    print("测试画廊API...")
    url = "http://localhost:8000/api/v1/projects/public/list"
    params = {
        "page": 1,
        "page_size": 12,
        "sort_by": "created_at",
        "sort_order": "desc"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        return response.status_code
    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    test_gallery_api()
