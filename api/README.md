<!--
 * @Author: '浪川' '1214391613@qq.com'
 * @Date: 2026-04-02 17:07:58
 * @LastEditors: '浪川' '1214391613@qq.com'
 * @LastEditTime: 2026-05-11 15:11:15
 * @FilePath: /api/README.md
 * @Description: 
 * 
 * Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
-->

启动 celery 服务

```sh
uv run celery -A app.core.celery:celery_app worker --pool=threads --concurrency=10 --loglevel=info
```
