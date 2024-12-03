# Agent说明

## 本项目说明
本项目实现了一个基于 **gRPC** 的问答服务，通过利用大型语言模型（LLM）支持类似 React 风格的 **Chain of Thought (CoT)** 推理，同时还能动态生成柱状图。

### 1. **功能概述**
代码的目标是解析用户输入的文本问题和文档内容，借助 LLM 的推理能力解决问题。如果 LLM 的推理需要可视化数据分析（柱状图），系统可以动态生成图表并返回给用户。

---

### 2. **主要逻辑与步骤**

#### (1) **输入解析**
```python
question = request.question
file_data = request.file_data.decode("utf-8")
```
- **`request.question`**: 用户提出的问题。
- **`request.file_data`**: 用户上传的文件内容，假设是一个 **txt 文件**，这里解码为字符串。

---

#### (2) **Chain of Thought Prompt 模板**
```python
react_cot_prompt_template = """
文档内容：{document}
...
<Question>: {input}
{agent_scratchpad}"""
```
- Prompt 模板为 LLM 提供上下文，包括：
  - **文档内容 (`document`)**: 用户上传的文件。
  - **问题 (`input`)**: 用户的提问。
  - **思考链 (`agent_scratchpad`)**: 记录 LLM 的推理过程，类似一个共享笔记本，便于迭代推理。

Prompt 中约定了一个特殊的格式，分为：
- `<Question>`：问题描述。
- `<Thought>`：模型的思考过程。
- `<Action>` 和 `<Action Input>`：指定模型是否需要调用工具（如绘图工具 `plot`）。
- `<Observation>`：工具的执行结果反馈给模型。
- `<Final Answer>`：最终问题的答案。

> 这个结构引导 LLM 推理时严格按照步骤执行，并通过工具（`plot`）实现特定功能。

---

#### (3) **CoT 推理循环**
```python
while not is_final_answer:
    prompt = react_cot_prompt_template.format(
        input=question,
        agent_scratchpad=agent_scratchpad,
        document=file_data
    )
    cot_output = llm_invoke(prompt)
```
**循环描述**：
1. **动态 Prompt 填充**：
   每轮循环将最新的上下文（文档、问题、推理链）格式化填入 Prompt。

2. **调用 LLM (`llm_invoke`)**：
   使用大型语言模型（LLM）生成输出，返回模型基于 Prompt 的推理结果（`cot_output`）。

3. **解析模型输出**：
   将模型返回的输出按特定标签格式解析为结构化数据（如 `<Thought>`, `<Action>` 等）。

---

#### (4) **Action 执行逻辑**
```python
if "plot" in parsed_data["Action"]:
    try:
        action_data = json.loads(parsed_data["Action Input"])
        x = action_data["x"]
        y = action_data["y"]

        fig, ax = plt.subplots()
        ax.bar(x, y)
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png")
        plt.close(fig)
        img_buffer.seek(0)
        image_data = img_buffer.read()
        observation = "Plot generated successfully."
```
- 当 LLM 决定调用工具（`plot`）：
  1. **解析输入**：
     - 提取 `<Action Input>` 的 JSON 格式内容，包括 x 和 y 轴的数据。
  2. **绘图**：
     - 使用 `matplotlib` 绘制柱状图，并将图像保存到内存缓冲区（`io.BytesIO`）。
  3. **生成反馈**：
     - 将绘图状态反馈到 `<Observation>` 中。

---

#### (5) **Final Answer**
```python
if is_final_answer:
    agent_scratchpad += f"<Final Answer>: {parsed_data['Final Answer']}\n"
```
- LLM 如果返回 `<Final Answer>`，表示推理结束。
- 将答案记录到 `agent_scratchpad`，以便终止循环。

---

#### (6) **响应返回**
```python
return agent_example_pb2.QueryResponse(
    has_text=bool(parsed_data["Final Answer"]),
    text_answer=parsed_data["Final Answer"] if parsed_data["Final Answer"] else "",
    has_image=bool(image_data),
    image_data=image_data if image_data else b"",
)
```
- 根据是否有答案（文本/图片）构造 gRPC 响应对象 `QueryResponse` 返回给用户。

---

## react风格详解篇

### **React 风格的简介**
**React 风格**是一种 **Reasoning + Acting (推理+行动)** 的范式，用于引导大语言模型（LLM）逐步分解复杂问题，并与工具或环境交互完成任务。这种风格强调：
1. **逐步推理**（Reasoning）：模型记录每一步的思考过程，明确当前的任务。
2. **行动选择**（Acting）：当推理需要工具或外部环境的帮助时，模型通过调用指定的工具完成特定子任务。
3. **反馈闭环**：根据工具的返回结果，模型继续推理，直到完成任务。

React 风格常用于处理复杂任务，如多步骤推理、工具调用和动态任务决策。

---

### **React 风格的核心逻辑**
React 风格的核心逻辑如下：
1. 将任务分解为多个可解释步骤。
2. 在每个步骤明确：
   - 当前需要解决的子问题。
   - 是否需要调用工具。
   - 工具调用的参数（如果需要）。
3. 根据工具返回的结果调整推理方向。
4. 最终得出答案。

---

### **Prompt 的变化过程**
React 风格的 prompt 会在每一轮根据模型的推理更新，从而形成动态交互。以下描述传递给 LLM 的 prompt 是如何随着推理过程和工具调用结果不断变化的。

---

#### 1. **初始 Prompt**
当模型第一次被调用时，Prompt 包括：
- **文档内容**：需要上下文的完整信息（如用户上传的文件内容）。
- **用户问题**：模型需要回答的主问题。
- **推理模板**：引导模型如何进行推理和行动。
  
##### 示例：
```plaintext
文档内容：本次内容为《企业财报》，其中包括公司过去五年的收入增长情况。
请你根据文档内容，回答问题。你可以使用以下工具：
- plot: 用于绘制柱状图图像。
  - 输入格式为一个字典，分别输入x轴和y轴数据，例如： {"x": ["x1", "x2", "x3"], "y": [5, 3, 1]}。

你应当只在需要调用工具的时候调用，其他时候都不应该调用。

请按照以下格式进行操作：

<Question>:
用户的问题：过去五年中收入的增长趋势是什么？
<Thought>:
你的思考过程，记录你下一步计划的内容  
<Action>:
你要使用的工具名，应该是以下工具之一 [ plot ] 
<Action Input>:
提供给行动的输入内容  
<Observation>: 
执行行动后的观察结果（不应由你返回，应当由工具返回）
...（这个 "<Thought>/<Action>/<Action Input>/<Observation>" 可以重复很多次）  
<Thought>: 
我现在知道最终答案了  
<Final Answer>: 
原始问题的最终答案  

让我们开始解决问题吧！
---
<Question>: 过去五年中收入的增长趋势是什么？
<Thought>:
需要检查文档内容，提取过去五年的收入数据。
```

---

#### 2. **第一轮推理**
模型接收到初始 Prompt 后，生成推理内容，例如：

##### 模型返回：
```plaintext
<Thought>: 
文档中提到了过去五年的收入数据。我需要提取这些年份及其对应的收入值，并绘制柱状图。
<Action>: 
plot
<Action Input>: 
{"x": ["2018", "2019", "2020", "2021", "2022"], "y": [100, 150, 200, 250, 300]}
```

---

#### 3. **工具调用后 Prompt 的更新**
工具（`plot`）生成柱状图，并返回结果。这一结果会作为新的 `<Observation>` 添加到 Prompt 中，供下一轮推理使用。

##### Prompt 更新：
```plaintext
文档内容：本次内容为《企业财报》，其中包括公司过去五年的收入增长情况。
请你根据文档内容，回答问题。你可以使用以下工具：
- plot: 用于绘制柱状图图像。
  - 输入格式为一个字典，分别输入x轴和y轴数据，例如： {"x": ["x1", "x2", "x3"], "y": [5, 3, 1]}。

你应当只在需要调用工具的时候调用，其他时候都不应该调用。

请按照以下格式进行操作：

<Question>:
用户的问题：过去五年中收入的增长趋势是什么？
<Thought>:
需要检查文档内容，提取过去五年的收入数据。
<Action>: 
plot
<Action Input>: 
{"x": ["2018", "2019", "2020", "2021", "2022"], "y": [100, 150, 200, 250, 300]}
<Observation>: 
柱状图生成成功。
<Thought>: 
图表显示收入在过去五年呈现持续增长的趋势。
我现在知道最终答案了。
<Final Answer>: 
收入在过去五年中每年都增长，趋势呈现稳定上升。
```

---

#### 4. **最终 Prompt 和返回结果**
当模型生成 `<Final Answer>` 时，推理结束，返回结果。

##### Prompt 最终形态：
```plaintext
文档内容：本次内容为《企业财报》，其中包括公司过去五年的收入增长情况。
请你根据文档内容，回答问题。你可以使用以下工具：
- plot: 用于绘制柱状图图像。
  - 输入格式为一个字典，分别输入x轴和y轴数据，例如： {"x": ["x1", "x2", "x3"], "y": [5, 3, 1]}。

你应当只在需要调用工具的时候调用，其他时候都不应该调用。

请按照以下格式进行操作：

<Question>:
用户的问题：过去五年中收入的增长趋势是什么？
<Thought>:
需要检查文档内容，提取过去五年的收入数据。
<Action>: 
plot
<Action Input>: 
{"x": ["2018", "2019", "2020", "2021", "2022"], "y": [100, 150, 200, 250, 300]}
<Observation>: 
柱状图生成成功。
<Thought>: 
图表显示收入在过去五年呈现持续增长的趋势。
我现在知道最终答案了。
<Final Answer>: 
收入在过去五年中每年都增长，趋势呈现稳定上升。
```

返回结果：
- **文本答案**：
  ```plaintext
  收入在过去五年中每年都增长，趋势呈现稳定上升。
  ```
- **图像数据**：
  生成的柱状图作为二进制数据返回。

---

### **总结：React Prompt 的动态变化**
1. Prompt 随着任务进展和工具调用的结果动态更新，模拟了逐步推理的过程。
2. 每轮 Prompt 包含先前的推理历史（`agent_scratchpad`），帮助模型在上下文中连续推理。
3. 模型依据 `<Thought>` 判断是否需要工具，通过 `<Action>` 指定工具类型，通过 `<Action Input>` 提供工具参数。
4. 工具返回结果后更新 `<Observation>`，帮助模型调整推理方向，最终生成 `<Final Answer>`。


## 名词解释

### **什么是工具（Tools）**
**工具**是一个可以由大型语言模型（LLM）调用的外部功能模块，用来完成 LLM 无法直接完成的特定任务。工具可以是：
1. **Python 函数**：执行计算、绘图、数据处理等操作。
2. **RPC 服务**：通过远程过程调用完成跨进程或分布式环境中的任务。
3. **其他服务**：如数据库查询、API 调用等。

工具通常由以下三部分组成：
1. **名称**：唯一标识工具。
2. **输入格式**：工具接受的参数形式，通常是 JSON 或结构化数据。
3. **输出结果**：工具的执行结果，反馈给 LLM。

---

### **工具的调用方式**
#### **1. 使用 Python 函数**
Python 函数工具直接在本地运行，具有以下特点：
- 输入是 JSON 格式数据。
- 执行特定逻辑（如绘图、计算）。
- 输出执行结果。

**调用过程：**
- LLM 通过生成 `<Action>` 和 `<Action Input>` 告诉系统需要调用工具。
- 系统解析工具名称和输入，执行对应的函数。
- 执行结果返回给 LLM。

**示例：绘制柱状图**
```python
import json
import matplotlib.pyplot as plt
import io

def plot_tool(input_data: str) -> str:
    """
    用于绘制柱状图的工具。
    :param input_data: JSON 格式的输入，例如 {"x": ["A", "B", "C"], "y": [1, 2, 3]}
    :return: 返回图像的路径或状态信息。
    """
    try:
        data = json.loads(input_data)  # 解析 JSON 数据
        x = data["x"]
        y = data["y"]
        # 检查 x 和 y 长度
        if len(x) != len(y):
            return "Error: Length of x and y must be the same."

        # 绘制柱状图
        fig, ax = plt.subplots()
        ax.bar(x, y)
        ax.set_title("Bar Chart")

        # 保存图像到内存缓冲区
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)

        return "Plot generated successfully."
    except Exception as e:
        return f"Error: {str(e)}"
```

调用流程：
1. LLM 生成：
   ```plaintext
   <Action>: plot
   <Action Input>: {"x": ["2018", "2019", "2020"], "y": [100, 200, 300]}
   ```
2. 系统将 JSON 数据解析为 `{"x": ["2018", "2019", "2020"], "y": [100, 200, 300]}`。
3. 调用工具 `plot_tool(input_data)`。
4. 将返回结果（如 `"Plot generated successfully."`）反馈给 LLM。

---

#### **2. 使用 RPC 服务**
RPC（远程过程调用）用于跨进程或分布式环境中调用工具，通常在需要高性能或跨语言的情况下使用。

**调用过程：**
- 系统通过 gRPC 或类似协议与远程服务交互。
- LLM 提供的 `<Action Input>` 被序列化为 RPC 请求参数。
- 远程服务执行操作，并将结果返回。

**示例：通过 RPC 计算加法**
定义一个 RPC 服务，用于执行加法：
```python
# server.py
import grpc
from concurrent import futures
import math_pb2
import math_pb2_grpc

class MathService(math_pb2_grpc.MathServicer):
    def Add(self, request, context):
        result = request.a + request.b
        return math_pb2.AddReply(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    math_pb2_grpc.add_MathServicer_to_server(MathService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

客户端调用：
```python
import grpc
import math_pb2
import math_pb2_grpc

def rpc_add_tool(input_data: str) -> str:
    """
    使用 RPC 调用加法服务的工具。
    :param input_data: JSON 格式，例如 {"a": 3, "b": 5}
    :return: 计算结果。
    """
    data = json.loads(input_data)
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = math_pb2_grpc.MathStub(channel)
        response = stub.Add(math_pb2.AddRequest(a=data["a"], b=data["b"]))
    return f"Addition Result: {response.result}"
```

调用流程：
1. LLM 生成：
   ```plaintext
   <Action>: add
   <Action Input>: {"a": 3, "b": 5}
   ```
2. 系统解析工具名称和输入，调用 RPC 服务：
   ```python
   result = rpc_add_tool('{"a": 3, "b": 5}')
   ```
3. 远程服务返回结果 `Addition Result: 8`。

---

### **工具调用的完整说明**
以下是使用工具的标准流程说明。

#### **工具定义**
工具的基本组成部分：
1. **名称**：工具的唯一标识符（如 `plot`, `add`）。
2. **输入格式**：工具需要的参数，通常为 JSON 格式。
3. **功能描述**：工具的作用及其返回值。

**示例工具列表**：
```json
{
    "tools": [
        {
            "name": "plot",
            "description": "用于绘制柱状图。",
            "input_format": {"x": "list of strings", "y": "list of integers"}
        },
        {
            "name": "add",
            "description": "远程调用服务进行加法运算。",
            "input_format": {"a": "integer", "b": "integer"}
        }
    ]
}
```

---

#### **调用步骤**
1. **LLM 推理生成 Action**：
   LLM 在推理过程中决定调用工具，生成 `<Action>` 和 `<Action Input>`。

2. **系统解析工具调用**：
   - 根据 `<Action>` 确定工具类型。
   - 根据 `<Action Input>` 提供的数据，调用对应工具。

3. **工具执行并返回结果**：
   工具完成任务后，将结果反馈给系统。

4. **反馈结果给 LLM**：
   结果以 `<Observation>` 的形式加入上下文，帮助 LLM 调整推理。

---

#### **调用示例（综合）**
Prompt 示例：
```plaintext
<Question>: 求和 5 和 10
<Thought>: 
我需要使用加法工具完成计算。
<Action>: add
<Action Input>: {"a": 5, "b": 10}
```

系统调用工具：
```python
result = rpc_add_tool('{"a": 5, "b": 10}')
# result = "Addition Result: 15"
```

反馈结果：
```plaintext
<Observation>: Addition Result: 15
<Thought>: 
计算完成。我现在知道答案了。
<Final Answer>: 15
```

---

### 注意
为了让大模型能够调用工具，你需要详细描述调用工具的**关键词** ，工具调用的时机，工具**输入输出**，如果有必要还需要给出**示例**。