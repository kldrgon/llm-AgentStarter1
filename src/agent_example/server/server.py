import grpc
import argparse
from concurrent import futures
from agent_example.server.service import FileBasedQAService
from agent_example.generated import agent_example_pb2_grpc


def serve(port = 0):
    """
    启动 gRPC 服务
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_example_pb2_grpc.add_FileBasedQAServicer_to_server(FileBasedQAService(), server)

    # 自动分配端口支持
    bind_address = f"[::]:{port}"
    server.add_insecure_port(bind_address)
    bound_port = server._state.server._port
    print(f"gRPC server is running on port {bound_port}...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    # 命令行参数支持
    parser = argparse.ArgumentParser(description="Run the gRPC server.")
    parser.add_argument("--port", type=int, default=0, help="Port to run the gRPC server on. Use 0 for auto-assign.")
    args = parser.parse_args()

    serve(args.port)
