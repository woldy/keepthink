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

def llm(prompt, client,model,system_str= "你是人工智能助手",max_tokens=16384):
    """ 执行 LLM 任务，并返回响应 """
    stream = client.chat.completions.create(
        model=model,  # your model endpoint ID
        messages=[
            {"role": "system", "content":system_str},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        stream=True
    )
    response = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        response += chunk.choices[0].delta.content
    return response

def process_prompts(prompts, client, model, system_str, max_tokens=16384, max_workers=5, progress_bar=None):
    """ 并行执行 LLM 任务，并保持顺序 """
    results = [None] * len(prompts)

    def worker(index, prompt):
        result = llm(prompt, client, model=model, system_str=system_str, max_tokens=max_tokens)
        results[index] = result
        if progress_bar:
            progress_bar.update(1)  # 直接更新进度条，无需yield

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, index, prompt) for index, prompt in enumerate(prompts)]
        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            future.result()  # 捕获可能的异常

    return results

def keepthink(prompt, client, background="", rule="", max_workers=3, split_n=0, min_length=0,model="deepseek-r1-250120",system_str= "你是人工智能助手",max_tokens=16384,thinkpromt_path="",max_retries=10):
    """ 任务拆分 + 进度显示 """
    yield {"type": "log", "content": "\n=== 任务初始化 ==="}
    


    if split_n > 0:
        prompt += f"\n本任务需拆分成 {split_n} 个任务进行"
    if min_length > 0:
        prompt += f"\n本任务输出不少于 {min_length} 字"
    
    if split_n > 0 and min_length > 0:
        length=int(min_length/split_n)
    else:
        length=2000


    yield {"type": "log", "content": f"加载思考模板中…"}
    think_prompt = load_thinkpromt(thinkpromt_path)
    if not think_prompt:
        yield {"type": "log", "content": f"错误：加载思考模板失败: {str(e)}"}
        return None

    think_prompt = think_prompt.replace("{#task#}", prompt)
    think_prompt = think_prompt.replace("{#background#}", background)
    think_prompt = think_prompt.replace("{#rule#}", rule)

    context="【已生成章节】\n以下为已生成章节内容，供参考，请注意新生成内容与之前内容的连贯性\n"

    for i in range(0,max_retries):
        if i>0:
            yield {"type": "log", "content": f"调用 LLM 进行任务拆分，正在进行第{i+1}次任务拆分尝试..."}
        else:
            yield {"type": "log", "content": f"调用 LLM 进行任务拆分..."}
        think = llm(think_prompt, client,model=model,system_str= system_str,max_tokens=max_tokens)
        
        # 数据提取
        unified_rules = ""
        prompts_array = []

        # print("解析 LLM 生成的任务拆分...")
        sections = think.split('### ')[1:]  # 丢弃第一个空元素

        for section in sections:
            section = section.strip()
            if section.startswith('Prompt'):
                prompt_num, content = section.split('\n', 1)
                prompts_array.append(content.strip())
        if len(prompts_array)>=split_n-1 and not "篇幅" in "think":
            yield {"type": "log", "content": f"任务拆分完成，共 {len(prompts_array)} 个子任务"}
            break
        else:
            yield {"type": "log", "content": "⚠️ 检测到降智响应，即将重试..."}


    yield {"type": "log", "content": think}

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
5、仅对本次任务要求进行回答，无需回答其它部分，无需输出任务编号，也不需要对本次内容进行任何解释，包括不要使用括号对本章节进行注释，仅输出正文内容即可
6、本次回答内容不低于{length}字，参考【被拆分成的子任务概览】，适当对上一模块有一些承接，避免直接切入过于突兀

【统一规则】
上下文一致性：所有子任务需保持上下文一致性，确保合并后内容连贯。
风格统一：确保所有子任务的风格（如语言风格、视觉风格）一致。
术语统一：确保所有子任务使用的术语一致，避免混淆。
逻辑衔接：子任务之间的逻辑需紧密衔接，避免信息断层。
可读性强：语言简洁明了，避免过度使用复杂句式或专业术语。
完整性：确保所有子任务合并后内容完整，无遗漏。
可执行性：确保每个子任务的内容可实际执行或操作。
总结与展望：最后一个子任务需对整体任务进行总结，并展望未来方向。
图示与文字结合：每个子任务需包含相应的图示，并与文字说明互为补充。
避免信息冗余：确保每个子任务的信息量适中，避免重复或无关内容。
"""
        new_prompts.append(new_prompt)

    # 进度条在 keepthink 里控制
    yield {"type": "log", "content":"\n开始并行执行子任务..."}
    responses=[]
    if max_workers>0:#多线程
        with tqdm(total=len(new_prompts), desc="Processing Tasks", unit="task") as progress_bar:
            responses = process_prompts(new_prompts, client, max_workers=max_workers, progress_bar=progress_bar,model=model,system_str= system_str,max_tokens=max_tokens)
    else:
        for new_prompt in new_prompts:
            content = llm(new_prompt+context, client,model=model,system_str= system_str,max_tokens=16384)
            context=context+content+"\n" #记录本次返回
            yield {"type": "log", "content":content}
            responses.append(content)
    yield {"type": "log", "content":"所有任务执行完毕！"}
    yield {"type": "result", "content":responses}
    return responses

