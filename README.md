## 一、KeepThink简介
**KeepThink** 是一个大模型任务自动拆分的工具，支持python库调用和WEBUI两种方式。

git仓库：https://github.com/woldy/keepthink

安装方式

    pip install keepthink

或

    pip install keepthink --index-url https://pypi.org/simple

由于这是一个新库，很多镜像未必有缓存，所以建议指定从pypi官网下载。

但理论上 pip install keepthink 也是OK的，安装起来非常简便。


## 二、KeepThink库的使用

keepthink本身是个python库，因此支持引用后直接调用函数

基础使用
    
    from openai import OpenAI
    
    from keepthink.chat import keepthink
    
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
    
    for item in gen:
    
        if item["type"]=="log":
    
            print(f"[LOG] {item['content']}")
    
        elif item["type"] == "result":
    
            for i, result in enumerate(item["content"], 1):
    
                print(f"\n【子任务 {i}】输出：\n{result}")

![image](https://github.com/user-attachments/assets/e7d6a12a-c564-49fb-aa0b-2eabe2c8242c)

## 三、高级使用

deepthink函数原型及参数如下：

    def keepthink(
    
        prompt,                 # [必填] 用户提示输入，主任务
    
        client,                 # [必填] API 客户端实例
    
        background="",          # 背景上下文信息
    
        rule="",                # 生成约束规则
    
        max_workers=3,          # 并行工作线程数，为0则取消并行
    
        split_n=0,              # 任务分割数量 (0=自动分割)
    
        min_length=0,           # 生成总内容最小长度
    
        model="deepseek-r1-250120",  # 使用的AI模型名称
    
        system_str="你是人工智能助手",  # 系统角色定义
    
        max_tokens=16384,       # 单次生成最大token数
    
        thinkpromt_path="",     # 自定义提示模板文件路径
    
        max_retries=10          # 降智最大重试次数
    
    )

注max_workers=0时，任务不会并行处理，但是每次任务会携带上次任务的上下文信息，整体生成的内容会更自然，适合需要上下文连贯的场景，比如小说等。

    from openai import OpenAI
    
    from keepthink.chat import keepthink
    
    client = OpenAI(
    
        api_key="******",
    
        base_url="https://ark.cn-beijing.volces.com/api/v3",
    
    )
    
    prompt="写一篇《量化之神卡卡西》的小说，用来将卡卡西通过使用写轮眼，观察股市涨跌，成为一方金融大鳄的故事"
    
    rule="用鲁迅的风格来写"
    
    gen = keepthink(
    
        prompt=prompt,
    
        client=client,
    
        rule=rule, 
    
        max_workers=3, 
    
        split_n=3, 
    
        background="卡卡西和玩偶姐姐是好朋友，玩偶姐姐教卡卡西炒币。",
    
        min_length=1000,
    
        model="deepseek-r1-250120",
    
        system_str= "你是目标领域专家，你是大佬，你要好好思考。",
    
        max_tokens=16384,
    
        max_retries=10 
    
    )
    
    for item in gen:
    
        if item["type"] == "log":
    
            print(f"[LOG] {item['content']}")
    
        elif item["type"] == "result":
    
            for i, result in enumerate(item["content"], 1):
    
                print(f"\n【子任务 {i}】输出：\n{result}")

![image](https://github.com/user-attachments/assets/77f2d6d3-f9b4-45b5-a177-cdec9a0bdf86)

四、WEBUI
keepthink自带了一个WEB UI客户端，可直接启用：

    keepthink
    
![image](https://github.com/user-attachments/assets/f0356e11-8c01-4075-96f8-ab4361c877d2)

    keepthink --port 8888 --host 0.0.0.0

![image](https://github.com/user-attachments/assets/73d46df7-51aa-4f23-8daf-a764dfb627e0)

WEBUI启动后，就会显示WEBUI页面

![image](https://github.com/user-attachments/assets/177f147b-22e7-462a-bbec-aee85e7f035d)

点击创建新话题，即可填写对应参数。

**注意此模式下要设置APIKEY**

![image](https://github.com/user-attachments/assets/e88d05f9-36fb-4d0a-a5ca-579a04495d2f)

结果如下：

![image](https://github.com/user-attachments/assets/3bf32d9b-9057-4f31-9845-61be2f4dc0b5)

![image](https://github.com/user-attachments/assets/248c3ee9-a771-4afe-a35f-17209c901106)

## 四、其它案例

解释多因子量化

![image](https://github.com/user-attachments/assets/898d9db7-22ba-4c2a-a24f-30d752ec7135)

![image](https://github.com/user-attachments/assets/2ebcd4a7-3415-4cfa-94f4-9bcecbadf587)

生成A股复盘文章

![image](https://github.com/user-attachments/assets/197e0097-b4f5-469d-a69e-e293cda3f96b)

![image](https://github.com/user-attachments/assets/96d7786e-f457-412a-9749-dd419ba7795c)

## 五、未来展望

**一句话：我要尝试开发DeepResearch相关功能。**






