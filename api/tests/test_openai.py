import httpx

# 读取图像并转为 base64
# with open('your_image.jpg', 'rb') as f:
#     img_b64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    'model': 'qwen3:8b',
    'prompt': 'What is in this picture?',
    'stream': False,
    'images': [],  # 注意是列表
}

try:
    resp = httpx.post(
        'http://14.12.0.172:11434/api/generate',  # 使用默认端口 11434
        json=payload,
        timeout=30.0,
    )
    resp.raise_for_status()
    result = resp.json()
    print(result.get('response', 'No response field'))
except Exception as e:
    print(f'Error: {e}')
