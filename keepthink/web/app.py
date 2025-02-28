from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from openai import OpenAI
from keepthink.chat import keepthink
import traceback
import json
import time
import os

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
chat_cache = {}
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    chat_id = data.get('chat_id')
    chat_cache[chat_id] = data
    
    # 将请求参数保存到会话中，以便SSE接口使用
    request.environ['keepthink_params'] = data
    
    return jsonify({
        "status": "success",
        "message": "处理已开始，请查看实时日志",
        "chat_id": chat_id
    })

@app.route('/stream/<chat_id>', methods=['GET'])
def stream(chat_id):
    def generate():
        try:
            # 获取处理参数
            #params = request.environ.get('keepthink_params', {})
            params = chat_cache.get(chat_id)
            # 提取参数
            prompt = params.get('prompt', '')
            rule = params.get('rule', '')
            background = params.get('background', '')
            max_workers = int(params.get('max_workers', 0))
            split_n = int(params.get('split_n', 10))
            min_length = int(params.get('min_length', 10000))
            model = params.get('model', 'deepseek-r1-250120')
            system_str = params.get('system_str', '你是目标领域专家，你是大佬，你要好好思考。')
            max_tokens = int(params.get('max_tokens', 16384))
            max_retries = int(params.get('max_retries', 10))
            api_key = params.get('api_key', '')
            base_url = params.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3')
            # 初始化 OpenAI 客户端
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
            
            # 发送初始消息
            yield f"data: {json.dumps({'type': 'log', 'content': '开始处理请求...'})}\n\n"
            
            # 调用 keepthink 函数
            gen = keepthink(
                prompt=prompt,
                client=client,
                rule=rule,
                background=background,
                max_workers=max_workers,
                split_n=split_n,
                min_length=min_length,
                model=model,
                system_str=system_str,
                max_tokens=max_tokens,
                max_retries=max_retries
            )
            
            results = []
            
            for item in gen:
                #print(item)
                if item["type"] == "log":
                    # 发送日志信息
                    yield f"data: {json.dumps({'type': 'log', 'content': item['content']})}\n\n"
                elif item["type"] == "progress":
                    # 发送进度信息
                    yield f"data: {json.dumps({'type': 'progress', 'current': item['current'], 'total': item['total']})}\n\n"
                elif item["type"] == "result":
                    # 收集结果
                    results = item["content"]
                    
                    # 发送结果通知
                    yield f"data: {json.dumps({'type': 'log', 'content': '处理完成，正在整理结果...'})}\n\n"
            
            # 发送最终结果
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append({
                    "task_number": i,
                    "content": result
                })
            
            yield f"data: {json.dumps({'type': 'result', 'content': formatted_results})}\n\n"
            
            # 发送结束通知
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            # 发送错误信息
            traceback.print_exc()  #
            error_msg = str(e)
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=6888)