import ollama
import requests

# 定义代理服务器
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

# 定义一个文件读取工具函数
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return str(e)

# 定义所有可用的函数
available_functions = {
    'request': requests.request,
    'read_file': read_file,  # 添加读取文件的工具
}

messages=[{'role': 'user','content': 'get the https://huggingface.co/ webpage?'}]

def chatbootbytools(messages):
    # 调用 Ollama API 来执行任务
    response = ollama.chat(
        'llama3.1:8b',
        messages=messages,
        tools=[read_file, requests.request],  # 这里加入了 `read_file` 工具
    )

    # 处理工具调用
    for tool in response.message.tool_calls or []:
        function_to_call = available_functions.get(tool.function.name)
        
        if function_to_call == requests.request:
            # 处理 HTTP 请求
            url = tool.function.arguments.get('url')
            resp = function_to_call(
                method=tool.function.arguments.get('method'),
                url=url,
                proxies = proxies,
            )
            info = {'role': 'assistant','content': f"The source code of the webpage at {url} is: {resp.text[:5000]}, please briefly summarize the website's purpose"}
            messages.append(info)
            print("\n" + "="*20 + "\n"+"网页读取功能被触发" +"\n" + "="*20 + "\n")
            
        
        elif function_to_call == read_file:
            # 处理文件读取
            file_path = tool.function.arguments.get('file_path')
            content = function_to_call(
                file_path=file_path,
            )
            info = {'role': 'assistant','content': f'The content of document {file_path} is: {content}'}
            messages.append(info)
            print("\n" + "="*20 + "\n"+"文件读取功能被触发" +"\n" + "="*20 + "\n")
        
        else:
            print('Function not found:', tool.function.name)
    print(response['message']['content'])

def chatbootjson(stream: bool,messages):
    # 调用 Ollama API 来执行任务
    respose = ollama.chat(
        stream=stream,  # 启用流式输出
        model ='llama3.1:8b',
        messages=messages,
    )
    if stream:
        print('\n---------------stream-----------------------')
        for chunk in respose:
            # print(chunk)
            if not chunk['done']:
                print(chunk['message']['content'], end='', flush=True)
            else:
                print('\n')
                print('-----------------------------------------')
                print(f'总耗时：{chunk["total_duration"] / 1_000_000_000}s')
                print('-----------------------------------------')
    else:
        print('\n---------------all-----------------------')
        print(respose['message']['content'])
        print('-----------------------------------------')
        print(f'总耗时：{respose["total_duration"] / 1_000_000_000}s')
        print('-----------------------------------------')

        return respose['message']['content']

print(f"用户提问为：{messages[-1]['content']}")
chatbootbytools(messages)
print(f"用户提问为：{messages[-1]['content']}")
chatbootjson(stream=False,messages=messages)