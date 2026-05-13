"""
Author: '浪川' '1214391613@qq.com'
Date: 2026-04-02 17:07:58
LastEditors: '浪川' '1214391613@qq.com'
LastEditTime: 2026-05-13 11:05:57
FilePath: /api/main.py
Description: 创建FastAPI应用程序并定义根路由。

Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}
