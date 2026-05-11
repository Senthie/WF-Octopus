import requests

# 测试 /api/v1/celery/test 端点
print('测试 /api/v1/celery/test 端点...')
try:
    response = requests.post('http://localhost:9070/api/v1/celery/test?name=测试用户')
    print(f'状态码: {response.status_code}')
    print(f'响应内容: {response.text}')

    if response.status_code == 200:
        data = response.json()
        print(f'任务ID: {data.get("data", {}).get("task_id")}')
        print(f'任务状态: {data.get("data", {}).get("status")}')
except Exception as e:
    print(f'测试失败: {e}')

print('\n' + '=' * 50 + '\n')

# 测试 /api/v1/celery/fetch 端点
print('测试 /api/v1/celery/fetch 端点...')
try:
    response = requests.post('http://localhost:9070/api/v1/celery/fetch?name=异步任务')
    print(f'状态码: {response.status_code}')
    print(f'响应内容: {response.text}')

    if response.status_code == 200:
        data = response.json()
        task_id = data.get('data', {}).get('task_id')
        print(f'任务ID: {task_id}')

        # 等待几秒后检查任务状态
        import time

        time.sleep(2)

        print(f'\n检查任务状态 {task_id}...')
        status_response = requests.get(f'http://localhost:9070/api/v1/celery/fetch/{task_id}')
        print(f'状态码: {status_response.status_code}')
        print(f'任务状态: {status_response.text}')
except Exception as e:
    print(f'测试失败: {e}')
