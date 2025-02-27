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

### 安装keepthink
```bash
pip install keepthink --index-url https://pypi.org/simple
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
from openai import OpenAI
from keepthink.chat import keepthink


# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="***********",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 运行任务
x = keepthink(
    "写一篇《量化之神卡卡西》的小说，用来将卡卡西通过使用写轮眼，观察股市涨跌，成为一方金融大鳄的故事",
    client
)

# 输出最终结果
print("\n=== 最终任务结果 ===")
for i, result in enumerate(x, 1):
    print(f"\n【子任务 {i}】\n{result}")

```
![image](https://github.com/user-attachments/assets/19f2a8a8-6791-44c0-8b91-42c3ae94f5f9)

![image](https://github.com/user-attachments/assets/a557a0d4-07b8-4d39-8ecb-b7c2d0695e16)


## 高级功能

```python
from openai import OpenAI
from keepthink.chat import keepthink


# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="************",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 运行任务
background=""""
核心技能树映射表
火影技能	金融量化技能	能力转化逻辑
写轮眼·动态视力	高频交易算法优化	捕捉毫秒级K线波动，识别高频套利机会
写轮眼·记忆复制	策略逆向工程	通过观察对手交易记录反向推导量化模型
雷切	风险对冲闪电战	在0.3秒内完成跨市场对冲组合
土遁·心中斩首术	做空狙击	潜伏于市场底部突然发动做空攻击
水遁·水龙弹	流动性操控	制造虚假交易量引导资金流向
八门遁甲	杠杆暴击模式	开启200倍杠杆进行极限操作（需承受巨额穿仓风险）
通灵术·忍犬	舆情嗅探系统	帕克犬群实时监控全球财经媒体情绪指数
特色金融忍术设计
1. 写轮眼·量化之瞳（核心技能）
市场解构：将K线流动转化为查克拉经络图，直接观测庄家资金流向
时间折叠：在月读空间进行百次模拟交易，现实仅过1分钟
致命缺陷：连续使用会导致交易直觉钝化（参照卡卡西查克拉不足设定）
2. 金融幻术·泡沫蜃楼
制造虚假财报幻象引诱对手高价接盘
破解方式：拥有写轮眼可看穿PE ratio背后的真实现金流
3. 尾兽化·黑天鹅形态
当遭遇极端行情时唤醒体内"金融九尾"
特征：眼瞳变成血红色K线，交易终端浮现尾兽花纹
风险：可能反噬造成穿仓暴毙
对手技能矩阵
对手	代表技能	金融领域映射
大蛇丸	禁术·尸鬼封尽	做空机构恶意收购（需献祭自身资金）
宇智波鼬	天照·黑炎	做空报告引发目标公司股价自燃式暴跌
纲手	百豪之术·创造再生	危机企业重组专家
自来也	仙法·蛙组手	利用自然能量（宏观经济周期）预判
关键战役场景示例
「第三次量化战争」

战场：芝加哥商品交易所黑暗森林
卡卡西战术：
开启写轮眼解析原油期货波动率曲面
用水遁制造API库存数据假象
雷切突袭完成跨期套利
最终以土遁封住高盛量化团队的算法接口
深度设定建议
查克拉-资金转化系统：

1卡=1亿美元交易权限
施展S级忍术需消耗上忍30%的信用额度
金融血继限界：

宇智波家族掌控SEC（美国证监会）监察眼
日向家族拥有内幕交易白眼看穿术
暗部特别行动：

做空小组佩恩六道：每个傀儡控制不同衍生品市场
晓组织真正目标：收集九大央行尾兽完成全球QE

"""
prompt="写一篇《量化之神卡卡西》的小说，用来将卡卡西通过使用写轮眼，观察股市涨跌，成为一方金融大鳄的故事"
rule="不要有过多的修辞手段，要用最朴实无华的语言来书写这段剧情"
x = keepthink(
    prompt=prompt,
    client=client,
    background=background, 
    rule=rule, 
    max_workers=3, 
    split_n=10, 
    min_length=10000,
    model="deepseek-r1-250120",
    system_str= "你是周树人"
)

# 输出最终结果
print("\n=== 最终任务结果 ===")
for i, result in enumerate(x, 1):
    print(f"\n【子任务 {i}】\n{result}")

```

![image](https://github.com/user-attachments/assets/2c59de16-8255-40fe-b733-831c840ae2c3)

![image](https://github.com/user-attachments/assets/4fa07276-46c1-4073-b9bb-f052d06ea53b)

![image](https://github.com/user-attachments/assets/c29cdd58-c841-488a-b57d-48918de2bce8)



### 参数说明
| 参数 | 类型 | 说明 |
|------|------|-----|
| split_n | int | 任务拆分数量 |
| min_length | int | 最小输出长度 |
| max_workers | int | 最大并发数 |
| model | str | 大模型版本 |

懒得往上贴了自己看例子吧

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
