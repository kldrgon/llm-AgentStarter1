import grpc
from agent_example.generated import agent_example_pb2_grpc, agent_example_pb2
import base64


class FileBasedQAClient:
    def __init__(self, server_address="localhost:50051"):
        """
        初始化客户端，指定服务端地址
        """
        self.server_address = server_address

    def query_file(self, question, file_path):
        """
        发送请求到服务端，返回响应结果
        """
        # 读取文件内容
        with open(file_path, "rb") as f:
            file_data = f.read()

        # 创建 gRPC 通道
        with grpc.insecure_channel(self.server_address) as channel:
            stub = agent_example_pb2_grpc.FileBasedQAStub(channel)
            request = agent_example_pb2.QueryRequest(
                question=question,
                file_data=file_data
            )
            response:agent_example_pb2.QueryResponse = stub.QueryFile(request)

        # 解析响应
        return self._process_response(response)

    def _process_response(self, response : agent_example_pb2.QueryResponse):
        """
        处理服务端返回的响应
        """
        result = {
            "has_text": response.has_text,
            "text_answer": response.text_answer if response.has_text else None,
            "has_image": response.has_image,
            "image_data": None
        }

        if response.has_image:
            result["image_data"] = response.image_data

        return result

    def save_image(self, image_data, output_path="output_image.png"):
        """
        保存图像数据到本地文件
        """
        with open(output_path, "wb") as img_file:
            img_file.write(image_data)
        print(f"Image saved to {output_path}")


if __name__ == "__main__":
    # 初始化客户端
    client = FileBasedQAClient(server_address="localhost:50051")

    # 示例请求
    question = "What does the document analyze?"
    file_path = "example.txt"  # 替换为实际文件路径

    # 调用服务端接口
    response = client.query_file(question, file_path)

    # 输出结果
    print("Response:")
    if response["has_text"]:
        print(f"Text Answer: {response['text_answer']}")
    else:
        print("No text answer provided.")

    if response["has_image"]:
        print("Image data received. Saving to output_image.png...")
        client.save_image(response["image_data"])
    else:
        print("No image data provided.")
