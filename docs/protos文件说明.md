# protos文件说明.md

## 本项目服务描述篇
### 服务描述：FileBasedQA
该服务提供基于用户问题和上传文件的问答能力，支持返回文本回答和图像回答两种形式的结果。

---

### 输入（`QueryRequest`）

`QueryRequest` 是客户端调用服务时的输入消息，包含以下字段：

1. **`question` (string)**:  
   用户的问题，以字符串形式输入。

2. **`file_data` (bytes)**:  
   上传的文件内容，支持多种格式（如 PDF、文本文件等），以二进制数据的形式传递。

---

### 输出（`QueryResponse`）

`QueryResponse` 是服务返回的响应消息，包含以下字段：

1. **`has_text` (bool)**:  
   指示是否包含文本回答。  
   - `true`: 服务生成了文本形式的回答。
   - `false`: 服务未生成文本回答。

2. **`text_answer` (string)**:  
   文本回答内容（如果 `has_text` 为 `true`，则提供该字段）。

3. **`has_image` (bool)**:  
   指示是否包含图像回答。  
   - `true`: 服务生成了图像形式的回答。
   - `false`: 服务未生成图像回答。

4. **`image_data` (bytes)**:  
   图像的二进制数据（如果 `has_image` 为 `true`，则提供该字段）。

---

### 数据流示例：

1. **请求：**
   ```json
   {
     "question": "What is the summary of this document?",
     "file_data": "<binary data representing a txt>"
   }
   ```

2. **响应（文本回答示例）：**
   ```json
   {
     "has_text": true,
     "text_answer": "The document discusses the impact of climate change on biodiversity.",
     "has_image": false,
     "image_data": null
   }
   ```

3. **响应（图像回答示例）：**
   ```json
   {
     "has_text": false,
     "text_answer": "",
     "has_image": true,
     "image_data": "<binary data representing an image>"
   }
   ```

4. **响应（同时返回文本和图像回答）：**
   ```json
   {
     "has_text": true,
     "text_answer": "The document contains data on sales trends for 2023.",
     "has_image": true,
     "image_data": "<binary data representing an image of a chart>"
   }
   ```

## 使用方式

我们将以本服务的创建，逐步剖析每个命令及其文件结构的作用：

---

### **1. 创建文件结构**

```bash
mkdir -p src/agent_example/generated
```

#### **为什么需要创建文件结构？**

1. **模块化管理代码：**  
   - 将代码按功能和层次结构分开，比如 `src` 目录用来放项目的源代码，`agent_example` 是一个具体的模块，`generated` 专门存放通过 gRPC 工具生成的代码。

2. **易于维护：**  
   - 清晰的目录结构使得代码更容易被维护和扩展。
   - 例如，将生成的代码与手写的代码分开，避免后续的修改混乱。

3. **Python 的模块支持：**  
   - 在 Python 中，代码需要位于模块目录下才能被其他文件引用（必须有 `__init__.py` 文件，尽管现代版本的 Python 可以省略）。

---

### **2. 使用 `grpc_tools.protoc` 命令生成代码**

#### **命令的具体解释：**

```bash
poetry run python -m grpc_tools.protoc \
-Iprotos \
--pyi_out=src/agent_example/generated \
--python_out=src/agent_example/generated \
--grpc_python_out=src/agent_example/generated \
protos/agent_example.proto
```

1. **`poetry run python -m grpc_tools.protoc`**
   - 使用 `poetry` 来指定python虚拟环境，运行 `grpc_tools.protoc`。
   - `protoc` 是 Protocol Buffers（ProtoBuf）编译器的核心命令，用来将 `.proto` 文件编译为特定语言的代码。在这里是生成 Python 代码。

2. **`-Iprotos`**
   - 指定 `.proto` 文件所在的目录。
   - 这里假定你的 `.proto` 文件位于 `protos` 目录中。
   - `-I` 是包含路径参数的简写，它告诉编译器去哪里寻找 `agent_example.proto` 文件。

3. **`--pyi_out=src/agent_example/generated`**
   - 生成类型提示文件（`.pyi`），这对现代 Python 开发非常重要：
     - 方便 IDE 提供类型自动补全和错误检查。
     - 提升代码的可读性和开发效率。
   - 生成的 `.pyi` 文件与其他生成的代码一起存放在 `src/agent_example/generated` 目录下。

4. **`--python_out=src/agent_example/generated`**
   - 生成与数据结构相关的代码（`.pb2.py` 文件）。
   - 这些文件会包含：
     - 数据类型定义：将 `.proto` 文件中的消息定义（`message`）转换为 Python 的类。
     - 序列化与反序列化逻辑：用于处理 Protocol Buffers 的二进制格式。

5. **`--grpc_python_out=src/agent_example/generated`**
   - 生成与 gRPC 服务相关的代码（`.pb2_grpc.py` 文件）。
   - 这些文件包含：
     - 服务的接口定义（`Stub` 类，用于客户端调用）。
     - 服务的基类（`Servicer` 类，用于服务端实现）。

6. **`protos/agent_example.proto`**
   - 这是输入的 `.proto` 文件，定义了服务及其数据结构。
   - 参考目录 `protos/agent_example.proto`

---

### **3. 修改 `agent_example_pb2_grpc.py` 的导入路径**

#### **问题背景：**
gRPC 工具默认使用绝对路径导入生成的 `agent_example_pb2` 文件：
```python
import agent_example_pb2 as agent__example__pb2
```
由于我们的项目结构中没有将 `src/agent_example/generated` 目录配置为 Python 的模块搜索路径（如 `PYTHONPATH` 环境变量），这会导致导入失败。

#### **解决方法：**
将导入路径改为相对路径：
```python
from . import agent_example_pb2 as agent__example__pb2
```

#### **原因：**
- 使用相对路径可以确保模块在项目目录结构中正确引用。
- 在本例中，`agent_example_pb2_grpc.py` 和 `agent_example_pb2.py` 都位于 `generated` 目录下，因此使用 `from . import` 是最佳实践。

---

### **4. 各个路径和文件的作用**

| 路径/文件                          | 作用                                                                                     |
|------------------------------------|------------------------------------------------------------------------------------------|
| `src/`                             | 存放项目的所有源代码。                                                                  |
| `src/agent_example/`               | 一个具体的模块，管理与 `agent_example` 相关的代码。                                       |
| `src/agent_example/generated/`     | 存放 gRPC 工具生成的代码（数据结构和服务定义）。                                          |
| `protos/agent_example.proto`       | 定义服务和数据结构的 `.proto` 文件，供 gRPC 编译器生成代码时使用。                         |
| `agent_example_pb2.py`             | 包含数据结构的 Python 类，以及序列化/反序列化逻辑。                                       |
| `agent_example_pb2_grpc.py`        | 包含 gRPC 服务接口（Stub 和 Servicer）及相关的代码。                                      |
| `agent_example_pb2.pyi`            | 类型提示文件，用于 IDE 提供开发时的类型检查和补全。                                        |

---

### **5. 最终文件结构示例**

```plaintext
src/
└── agent_example/
    ├── generated/
    │   ├── agent_example_pb2.py          # 数据结构定义
    │   ├── agent_example_pb2_grpc.py     # 服务接口定义
    │   ├── agent_example_pb2.pyi         # 类型提示文件
    ├── __init__.py                       # 使 agent_example 成为 Python 包
protos/
└── agent_example.proto                   # 服务和数据定义文件
```

---

## 语法篇

### **Protocol Buffers (proto) 语法说明**

Protocol Buffers 是由 Google 开发的一种高效的数据序列化格式，通常用于远程过程调用（RPC）和数据存储。下面是 `proto3` 的语法说明，涵盖其核心功能和使用方法。

---

### **1. 基本结构**

#### **示例：**
```proto
syntax = "proto3";

package example; // 定义包名

message Person {
  string name = 1;  // 字符串类型
  int32 age = 2;    // 32位整数
  repeated string tags = 3; // 字符串数组
}

service ExampleService {
  rpc GetPerson (PersonRequest) returns (PersonResponse);
}

message PersonRequest {
  int32 id = 1; // 请求中包含的 ID
}

message PersonResponse {
  Person person = 1; // 响应中包含的 Person 对象
}
```

---

### **2. 关键字和语法**

#### **2.1. 必须的语法声明**
```proto
syntax = "proto3";
```
- 表示使用 `proto3` 语法版本。

---

#### **2.2. 包声明**
```proto
package example;
```
- 指定 `package` 名字，用于防止不同 proto 文件中的类型命名冲突。
- 生成的代码会基于包名构造命名空间，例如 Java 中会生成 `example` 包。

---

#### **2.3. 导入文件**
```proto
import "other.proto";
```
- 导入其他 proto 文件中的定义，以便复用。
- 文件路径相对于编译器运行时的 `-I` 参数路径。

---

### **3. 数据类型**

#### **3.1. 基本类型**
| 类型         | 描述                                        |
|--------------|---------------------------------------------|
| `double`     | 双精度浮点数                                |
| `float`      | 单精度浮点数                                |
| `int32`      | 有符号 32 位整数                            |
| `int64`      | 有符号 64 位整数                            |
| `uint32`     | 无符号 32 位整数                            |
| `uint64`     | 无符号 64 位整数                            |
| `sint32`     | 有符号 32 位整数，使用 ZigZag 编码           |
| `sint64`     | 有符号 64 位整数，使用 ZigZag 编码           |
| `fixed32`    | 固定大小的 32 位整数                        |
| `fixed64`    | 固定大小的 64 位整数                        |
| `sfixed32`   | 有符号固定大小的 32 位整数                  |
| `sfixed64`   | 有符号固定大小的 64 位整数                  |
| `bool`       | 布尔值，`true` 或 `false`                  |
| `string`     | 字符串（UTF-8 编码）                        |
| `bytes`      | 原始字节数据                                |

---

#### **3.2. 特殊类型**

- **枚举类型（`enum`）**
  ```proto
  enum Gender {
    UNKNOWN = 0; // 默认值，必须为 0
    MALE = 1;
    FEMALE = 2;
  }
  ```

- **复合类型（`message`）**
  - `message` 是 Protocol Buffers 中的核心数据结构：
    ```proto
    message Address {
      string street = 1;   // 街道
      string city = 2;     // 城市
      string postal_code = 3; // 邮政编码
    }
    ```

---

### **4. 字段规则**

#### **4.1. 标量字段**
- 标量字段的语法是：
  ```proto
  数据类型 字段名 = 字段编号 [字段选项];
  ```
- 示例：
  ```proto
  string name = 1;
  int32 age = 2;
  ```

#### **4.2. 数组字段（`repeated`）**
- 用 `repeated` 修饰字段表示该字段是一个数组。
- 示例：
  ```proto
  repeated string tags = 3;
  ```
  生成的代码会将此字段表示为列表。

#### **4.3. 字段编号**
- 每个字段必须有一个唯一的编号，范围是 1 到 2^29 - 1（主流建议 1 到 15 优先分配给常用字段）。
- 编号用于序列化和反序列化，因此一旦使用了编号，就不应随意更改。
- 编号 `19000-19999` 被保留，不能使用。

#### **4.4. 默认值**
- 在 `proto3` 中，所有字段都有默认值：
  - 数字类型：`0`
  - 字符串：`""`（空字符串）
  - 布尔类型：`false`
  - 枚举类型：第一个值
  - 数组：空列表

---

### **5. 服务定义**

- 使用 `service` 定义 gRPC 服务。
- 示例：
  ```proto
  service ExampleService {
    rpc GetPerson (PersonRequest) returns (PersonResponse);
  }
  ```
  - `rpc` 定义了一个远程过程调用（RPC）。
  - `GetPerson` 是方法名称。
  - 参数类型是 `PersonRequest`。
  - 返回类型是 `PersonResponse`。

---

### **6. 注释**

- 单行注释：
  ```proto
  // 这是单行注释
  ```
- 多行注释：
  ```proto
  /*
    这是多行注释
  */
  ```

---

### **7. 完整示例**

以下是一个完整的 `proto3` 示例，包含消息类型、服务和枚举。

```proto
syntax = "proto3";

package myapp;

// 导入其他 proto 文件
import "google/protobuf/timestamp.proto";

message User {
  int32 id = 1;               // 用户 ID
  string name = 2;            // 用户名
  Gender gender = 3;          // 性别
  repeated string interests = 4; // 兴趣列表
  google.protobuf.Timestamp created_at = 5; // 创建时间
}

enum Gender {
  UNKNOWN = 0; // 默认值，必须为 0
  MALE = 1;
  FEMALE = 2;
}

message GetUserRequest {
  int32 user_id = 1; // 请求用户 ID
}

message GetUserResponse {
  User user = 1; // 响应包含的用户信息
}

service UserService {
  rpc GetUser (GetUserRequest) returns (GetUserResponse); // 获取用户信息
}
```

---

### **8. 编译和生成代码**

1. 保存上述 `.proto` 文件，例如 `user.proto`。
2. 使用 `protoc` 命令生成代码：
   ```bash
   protoc -I. --python_out=. --grpc_python_out=. user.proto
   ```

这样就能生成数据结构和服务的 Python 代码，供客户端和服务端使用。

### **9. 注意
注意在本项目中如何使用protoc在上一篇中已有描述。