import os
import concurrent.futures
from openai import OpenAI
from tqdm import tqdm  # 进度条库
import pkg_resources 

def readfile(file_path, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：文件不存在 [{file_path}]")
    except PermissionError:
        print(f"错误：没有读取权限 [{file_path}]")
    except UnicodeDecodeError:
        print(f"错误：编码不匹配 [{encoding}]，尝试指定正确的编码")
    except Exception as e:
        print(f"未知错误：{str(e)}")
    return None

def load_thinkpromt(path=""):
    try:
        # 获取包内资源的绝对路径
        if path=="":
            path = pkg_resources.resource_filename(
                'keepthink',  # 包名
                os.path.join('prompts', 'think_prompt')  # 包内相对路径
            )
        return readfile(path)
    except Exception as e:
        print(f"加载思考模板失败: {str(e)}")
        return None

def llm(prompt, client,model,system_str= "你是人工智能助手"):
    """ 执行 LLM 任务，并返回响应 """
    stream = client.chat.completions.create(
        model=model,  # your model endpoint ID
        messages=[
            {"role": "system", "content":system_str},
            {"role": "user", "content": prompt},
        ],
        stream=True
    )
    response = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        response += chunk.choices[0].delta.content
    return response

def process_prompts(prompts, client,model,system_str, max_workers=5, progress_bar=None):
    """ 并行执行 LLM 任务，并保持顺序 """
    results = [None] * len(prompts)

    def worker(index, prompt):
        result = llm(prompt, client,model=model,system_str= system_str)
        results[index] = result
        if progress_bar:
            progress_bar.update(1)  # 让进度条前进 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for index, prompt in enumerate(prompts):
            future = executor.submit(worker, index, prompt)
            futures.append(future)
        concurrent.futures.wait(futures)

    return results

def keepthink(prompt, client, background="", rule="", max_workers=3, split_n=0, min_length=0,model="deepseek-r1-250120",system_str= "你是人工智能助手",thinkpromt_path=""):
    """ 任务拆分 + 进度显示 """
    print("\n=== 任务初始化 ===")
    
    if split_n > 0:
        prompt += f"\n本任务需拆分成 {split_n} 个任务进行"
    if min_length > 0:
        prompt += f"\n本任务输出不少于 {min_length} 字"
    
    print("加载思考模板...")
    think_prompt = load_thinkpromt(thinkpromt_path)
    if not think_prompt:
        print("错误：无法加载思考模板！")
        return None

    think_prompt = think_prompt.replace("{#task#}", prompt)
    think_prompt = think_prompt.replace("{#background#}", background)
    think_prompt = think_prompt.replace("{#rule#}", rule)

    print("调用 LLM 进行任务拆分...")
    think = llm(think_prompt, client,model=model,system_str= system_str)
    print(think)
    # 数据提取
    unified_rules = ""
    prompts_array = []

    print("解析 LLM 生成的任务拆分...")
    sections = think.split('### ')[1:]  # 丢弃第一个空元素

    for section in sections:
        section = section.strip()
        if section.startswith('Unified Rules'):
            rules = section.split('\n')[1:]  # 去掉标题行
            unified_rules = "\n".join(rules)
        elif section.startswith('Prompt'):
            prompt_num, content = section.split('\n', 1)
            prompts_array.append(content.strip())

    print(f"任务拆分完成，共 {len(prompts_array)} 个子任务")

    new_prompts = []
    for i, prompt2 in enumerate(prompts_array, 1):
        
        new_prompt = f"""
【背景】
{background}

【原始任务】
{prompt}

【被拆分成的子任务概览】
{content}

【规则】
{rule}

【本次任务要求】
{prompt2}
1、写出完整内容，不要省略，不要写摘要，要完整内容，要丰富
2、执行当前任务的时候，要与其它子任务相互配合，不要冲突或重复
3、仅输出正文内容，不需要有其它内容，正文内容要足够丰富且满足需求
4、尽量不要有太多的级联列表，多使用长文本的形式
5、仅对本次任务要求进行回答，无需回答其它部分，无需输出任务编号，也不需要对本次内容进行任何解释，仅输出对应内容即可
6、本次回答内容不低于2000字

【统一规则】
{unified_rules}
"""
        new_prompts.append(new_prompt)

    # 进度条在 keepthink 里控制
    print("\n开始并行执行子任务...")
    with tqdm(total=len(new_prompts), desc="Processing Tasks", unit="task") as progress_bar:
        responses = process_prompts(new_prompts, client, max_workers=max_workers, progress_bar=progress_bar,model=model,system_str= system_str)

    print("所有任务执行完毕！")
    return responses

