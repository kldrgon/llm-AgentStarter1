import json
import logging
import grpc
import io
import matplotlib.pyplot as plt

from agent_example.generated import agent_example_pb2_grpc, agent_example_pb2
from agent_example.server.utils import llm_invoke

class FileBasedQAService(agent_example_pb2_grpc.FileBasedQAServicer):
    def QueryFile(self, request: agent_example_pb2.QueryRequest, context: grpc.ServicerContext):
        """
        实现 gRPC 方法 QueryFile，支持 React 风格 Chain of Thought 推理
        """
        question = request.question
        file_data = request.file_data.decode("utf-8")  # 文件内容为txt格式

        # ========================
        # Chain of Thought Prompt
        # ========================
        react_cot_prompt_template = """
文档内容：{document}
请你根据文档内容，回答问题。你可以使用以下工具：
- plot: 用于绘制柱状图图像。
    - 输入格式为一个字典，分别输入x轴和y轴数据，例如：  {{"x": ["x1", "x2", "x3"], "y": [5, 3, 1]}}。

你应当只在需要调用工具的时候调用，其他时候都不应该调用。
    
请按照以下格式进行操作：

<Question>:
输入的问题，你需要回答的主要问题  
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

上述操作流程中有如下规则：
- 输出标记文字一定携带尖括号<>
- <Action>与<Action Input>只有你需要工具的时候成对出现。
- 输出<Action>与<Action Input>两个标签后你应当停止输出，等待工具给你返回<Observation>观测结果

让我们开始解决问题吧！
--- 
<Question>: {input}  
{agent_scratchpad}"""
                # 初始化变量
        is_final_answer = False
        agent_scratchpad = ""  # 用于拼接思考链
        image_data = None
        while not is_final_answer:
            # 格式化 Chain of Thought Prompt
            prompt = react_cot_prompt_template.format(
                input=question,
                agent_scratchpad=agent_scratchpad,
                document=file_data
            )

            # 调用智谱AI生成回答
            cot_output = llm_invoke(prompt)

            # 输出原始模型返回的结果
            logging.info("LLM Output: %s", cot_output)

            # 解析输出（支持多行标签内容）
            current_tag = None
            parsed_data = {  # 用于存储各标签的内容
                "Thought": "",
                "Action": "",
                "Action Input": "",
                "Observation": "",
                "Final Answer": "",
            }

            for line in cot_output.strip().split("\n"):
                line = line.strip()
                if line.startswith("<Question>:"):
                    question = line.replace("<Question>:", "").strip()
                    continue
                if line.startswith("<Thought>:"):
                    current_tag = "Thought"
                    parsed_data[current_tag] = line.replace("<Thought>:", "").strip()
                    continue
                if line.startswith("<Action>:"):
                    current_tag = "Action"
                    parsed_data[current_tag] = line.replace("<Action>:", "").strip()
                    continue
                if line.startswith("<Action Input>:"):
                    current_tag = "Action Input"
                    parsed_data[current_tag] = line.replace("<Action Input>:", "").strip()
                    continue
                if line.startswith("<Final Answer>:"):
                    current_tag = "Final Answer"
                    parsed_data[current_tag] = line.replace("<Final Answer>:", "").strip()
                    is_final_answer = True
                    continue

                # 如果当前行属于某个标签，则拼接内容
                if current_tag:
                    parsed_data[current_tag] += f"\n{line}"

            # 执行 `plot` 工具并生成 Observation
            if "plot" in parsed_data["Action"]:
                try:
                    # 解析 JSON 格式的 Action Input
                    action_input = parsed_data["Action Input"]
                    # 转换为 Python 数据结构
                    action_data = json.loads(action_input)

                    # 提取 x 和 y 数据
                    x = action_data["x"]
                    y = action_data["y"]

                    # 检查 x 和 y 的长度是否一致
                    if len(x) != len(y):
                        raise ValueError("Length of x and y must be the same.")

                    # 绘制柱状图
                    fig, ax = plt.subplots()
                    ax.bar(x, y)
                    ax.set_title("Generated Plot")
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format="png")
                    plt.close(fig)
                    img_buffer.seek(0)
                    image_data = img_buffer.read()
                    observation = "Plot generated successfully."
                except json.JSONDecodeError:
                    observation = "Failed to parse Action Input. Ensure it is a valid JSON object."
                    image_data = None
                except Exception as e:
                    observation = f"Failed to generate plot: {e}"
                    image_data = None
                    logging.error("Error generating plot: %s", e)

                # 动态生成 Observation
                agent_scratchpad += f"<Observation>: {observation}\n"

            # 如果是最终答案，直接添加到 agent_scratchpad
            if is_final_answer:
                agent_scratchpad += f"<Final Answer>: {parsed_data['Final Answer']}\n"
            logging.info(f"新一轮思考开始")
        # 返回响应
        return agent_example_pb2.QueryResponse(
            has_text=bool(parsed_data["Final Answer"]),
            text_answer=parsed_data["Final Answer"] if parsed_data["Final Answer"] else "",
            has_image=bool(image_data),
            image_data=image_data if image_data else b"",
        )
