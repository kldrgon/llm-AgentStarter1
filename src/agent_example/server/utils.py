
from zhipuai import ZhipuAI
import os
# 智谱AI的API密钥
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY")

# ========================
# 调用智谱AI生成回答
# ========================
def llm_invoke(prompt: str) -> str:
    """
    调用智谱AI生成回答
    """
    client = ZhipuAI(api_key=ZHIPU_API_KEY)
    response = client.chat.completions.create(
        model="glm-4-flashx",  # 使用指定模型。请注意，这个模型一定要足够强大。暂时测试至少得glm-4-flashx
        messages=[
            {"role": "system", "content": "你是一个文档问答专家，同时也是一个结构化输出的专业模型，你需要按照用户要求进行分析与输出。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
