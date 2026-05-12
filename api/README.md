<!--
 * @Author: '浪川' '1214391613@qq.com'
 * @Date: 2026-04-02 17:07:58
 * @LastEditors: '浪川' '1214391613@qq.com'
 * @LastEditTime: 2026-05-11 18:06:44
 * @FilePath: /api/README.md
 * @Description: 
 * 
 * Copyright (c) 2026 by '浪川' email: '1214391613@qq.com', All Rights Reserved.
-->

启动 Dramatiq worker（已将任务迁移至 Dramatiq）

```sh
# 激活虚拟环境后安装依赖：
pip install "dramatiq[redis]" "uvloop>=0.17.0"

# 启动示例 worker（根据需要调整模块/队列）
dramatiq app.tasks.inspection_dramatiq --processes 1 --threads 8
```
