# KeepThink - 基于大模型的任务分解与并行处理框架

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 项目概述

KeepThink 是一个基于大语言模型的智能任务处理框架，通过自动化任务拆分、并行处理与结果整合，帮助用户高效完成复杂生成任务。特别适用于长文本生成、多维度分析等需要分层处理的应用场景。

## 核心功能

✅ 智能任务分解  
✅ 多线程并行处理  
✅ 动态进度可视化  
✅ 自定义生成规则  
✅ 统一风格控制  
✅ 容错重试机制  

## 快速开始

### 安装依赖
```bash
pip install openai tqdm
```

### 项目结构
```
keepthink/
├── chat.py            # 核心处理模块
├── __init__.py
├── prompts/
│ └── think_prompt    # 任务拆分模板
└── setup.py
```

### 基础使用
```python
from keepthink import keepthink, client

responses = keepthink(
    prompt="写一篇《量化之神卡卡西》的小说",
    client=client,
    background="卡卡西通过写轮眼观察股市涨跌",
    max_workers=5,
    split_n=3,
    min_length=2000
)
```

### 配置说明
```python
# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="your_api_key_here",
    base_url="https://your.api.endpoint",
    request_timeout=30
)
```

## 高级功能

### 自定义拆分规则
```python
keepthink(
    ...
    rule="每章节需包含金融术语",
    system_str="你是有10年经验的财经作家"
)
```

### 进度监控
```python
with tqdm(total=split_n, desc="生成进度") as pbar:
    responses = keepthink(..., progress_bar=pbar)
```

## 开发指南

### 模板定制
修改 `prompts/think_prompt` 文件来自定义任务拆分逻辑：
```
{#task#} - 原始任务
{#background#} - 上下文背景
{#rule#} - 生成约束条件
```

### 参数说明
| 参数 | 类型 | 说明 |
|------|------|-----|
| split_n | int | 任务拆分数量 |
| min_length | int | 最小输出长度 |
| max_workers | int | 最大并发数 |
| model | str | 大模型版本 |

## 贡献指南
欢迎通过 Issue 提交建议或 PR 参与开发：
1. Fork 本项目
2. 创建特性分支
3. 提交代码变更
4. 发起 Pull Request

## 许可协议
本项目采用 [MIT License](LICENSE)
```

请根据实际需求：
1. 替换API配置信息
2. 补充think_prompt模板内容
3. 添加具体的使用示例
4. 完善贡献指南细节
5. 添加测试和文档说明
