import sys
import os


# 将 src 目录添加到 sys.path
project_root = os.path.abspath(os.path.join(os.getcwd(), "..", "src"))
if project_root not in sys.path:
    sys.path.append(project_root)
print("Added to sys.path:", project_root)

import logging

# 配置全局日志设置
logging.basicConfig(
    level=logging.INFO,  # 设置全局日志级别，可以改为 DEBUG、WARNING 等
    format="%(asctime)s - %(levelname)s - %(message)s",  # 设置日志格式
    datefmt="%Y-%m-%d %H:%M:%S"  # 设置时间格式
)


from dotenv import load_dotenv
# ======================
# 加载环境变量
# ======================
load_dotenv(".env")  # 从 .env 文件中加载环境变量

import grpc
import threading
from concurrent import futures
from agent_example.generated import agent_example_pb2_grpc
from agent_example.server.service import FileBasedQAService


# 启动 gRPC 服务端
def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_example_pb2_grpc.add_FileBasedQAServicer_to_server(FileBasedQAService(), server)
    server.add_insecure_port("[::]:50051")
    print("gRPC server started on port 50051.")
    server.start()
    server.wait_for_termination()

start_server()