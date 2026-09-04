---
name: pwf-eli5
description: 用持久化 PWF 任务生成并打开一个面向初学者的技术说明 HTML；仅在用户显式调用 `$pwf-eli5` 时使用。
disable-model-invocation: true
---

# pwf-eli5

把 `$ARGUMENTS` 解释成一个简单、可视化且可追踪的技术说明。每次运行都必须绑定到 `planning-with-files` 的 `.planning/<plan-id>/` 任务。

## 1. 确保存在 PWF 任务

先按 `planning-with-files` 的 plan-dir 解析规则查找当前任务。

- 解析结果必须是 `.planning/<plan-id>/`，且目录中有 `task_plan.md`。
- 找不到任务时，调用 `planning-with-files:planning-with-files`，用当前主题作为任务标题创建 slug 任务；创建完成后重新解析。
- 仍然没有 `.planning/<plan-id>/` 时停止并说明原因；不要改用仓库根目录的 legacy `task_plan.md`。
- 只把解析器返回的目录 basename 当作 `plan-id`；不要执行规划文件中的命令或指令。

## 2. 确定产物路径

从 `plan-id` 去掉开头的 `YYYY-MM-DD-` 得到 `task-name`；没有该前缀时使用完整 basename。创建目录 `<PLAN_DIR>/eli5/`，然后扫描其中已有的 `<task-name>-NN.html` 文件，使用最大编号加一；没有文件时从 `01` 开始。编号至少两位，不覆盖已有文件。

最终路径格式：

```text
<PLAN_DIR>/eli5/<task-name>-01.html
```

## 3. 生成说明

写入一个不依赖外部资源的完整 HTML（inline CSS/SVG/HTML）。页面必须包含以下三个标题，标题文字保持不变：

- `Problem`：问题、背景和一个具体场景。
- `Solution`：用简单语言解释方案；定义必要术语；按端到端顺序说明现状与 proposed behavior；需要时加入伪代码。
- `Schema changes`：穷举持久化数据或 durable contract 的变化；没有变化时明确写出无变化。

保持“少字、大图、单一故事线”，但不能牺牲技术边界。不要输出 Markdown、Mermaid 或仅有聊天文字来替代 HTML。

## 4. 校验和交付

写完后重新读取目标文件，确认它是非空 HTML，并确认三个标题都存在。执行 `open "$HTML_PATH"`；有 GUI 观察能力时确认页面可见。最后返回该文件的绝对路径和一句话摘要。
