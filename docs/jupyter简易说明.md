**Jupyter Notebook 简易使用教程**：

---

### Jupyter Notebook 简易使用教程（操作篇）

---

### 1. 启动 Jupyter Notebook

1. 打开终端或命令行。
2. 输入以下命令启动 Jupyter Notebook：
   ```bash
   jupyter notebook
   ```
3. 浏览器会自动打开 Notebook 的界面（如果没有打开，请手动访问 `http://localhost:8888`）。

4. 注意，由于本项目中使用了poetry管理python项目环境，所以需要使用
    ``` bash
    poetry run jupyter notebook
    ```
---

### 2. Jupyter Notebook 界面介绍

- **文件浏览器**：可以打开、重命名和管理文件。
- **新建文件**：点击右上角 "New" 按钮，新建一个 Python 3 的 Notebook。
- **代码单元格（Code Cell）**：用于输入并运行代码。
- **Markdown 单元格（Markdown Cell）**：用于编写说明文字或公式。

---

### 3. 常用操作步骤

#### 3.1 创建一个新 Notebook
1. 在文件浏览器中，点击右上角的 "New"，选择 "Python 3"。
2. 在新页面中，您就可以输入代码或笔记。

#### 3.2 运行代码
- 在代码单元格中输入代码后，按下 `Shift + Enter` 或点击工具栏上的 "Run" 按钮即可执行代码。

示例代码：
```python
print("Hello, Jupyter!")
```

运行结果会显示在单元格下方。

#### 3.3 切换单元格类型
- 默认单元格是代码单元格。如果需要改为 Markdown：
  1. 点击单元格。
  2. 按 `Esc`，然后按 `M`。
- Markdown 单元格可用于书写标题、公式或说明文字。

Markdown 示例：
```markdown
# 这是一级标题
## 这是二级标题
- 列表项 1
- 列表项 2
```

LaTeX 示例（公式）：
```markdown
$E = mc^2$
```

#### 3.4 保存文件
- 点击工具栏的保存按钮，文件会以 `.ipynb` 格式保存。

#### 3.5 导出文件
- 将 Notebook 导出为 HTML、PDF 等格式：
  点击菜单栏 `File` > `Download as`。

---

### 4. 常用快捷键

Jupyter Notebook 有丰富的快捷键，可以极大提升效率。以下是一些常用快捷键：

#### 命令模式（单元格外按 `Esc` 激活）
- **运行当前单元格并跳转到下一个**：`Shift + Enter`
- **插入单元格**：
  - 上方插入：`A`
  - 下方插入：`B`
- **删除单元格**：`DD`
- **切换单元格类型**：
  - 代码单元格：`Y`
  - Markdown 单元格：`M`

#### 编辑模式（单元格内按 `Enter` 激活）
- **运行代码**：`Ctrl + Enter`
- **取消输入**：`Esc`

---

### 5. 数据分析与可视化示例

以下是几个常见任务的代码示例：

#### 5.1 加载常用库
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

#### 5.2 绘制简单图表
```python
x = [1, 2, 3, 4]
y = [10, 20, 25, 30]

plt.plot(x, y)
plt.title("Simple Plot")
plt.show()
```

#### 5.3 处理数据文件
```python
df = pd.read_csv("example.csv")
print(df.head())
```

---

### 6. 关闭 Jupyter Notebook

1. 在命令行按 `Ctrl + C` 停止运行。
2. 关闭所有 Jupyter 的浏览器页面。

---

### 7. 提示与技巧

1. **常用代码模板**：在新建 Notebook 时，可以预先加载常用库，便于快速分析。
2. **善用 Markdown**：用 Markdown 编写说明，让 Notebook 更具可读性。
3. **按需导出**：Notebook 文件可以导出为 HTML、PDF 等多种格式，方便分享。

---

这份教程帮助您专注于 Jupyter Notebook 的实际使用和功能探索，希望对您有所帮助！

### 参考文档

- [官方文档](https://jupyter.org/documentation)
- [Markdown 语法教程](https://www.markdownguide.org/)

这就是 Jupyter Notebook 的简易入门教程！希望对您有帮助。