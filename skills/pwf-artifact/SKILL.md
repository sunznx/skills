---
name: pwf-artifact
description: 将用户指定的对话产物保存到当前 Planning with Files 任务目录。
argument-hint: "要保存的内容或文件路径"
disable-model-invocation: true
---

# PWF Artifact

用户调用本技能时，保存其明确指定的文本、代码、图表或现有文件。根据当前对话确定产物的完整内容；指代不清时先请用户指出具体内容。

1. 使用 `planning-with-files` 的 `resolve-plan-dir.sh` 解析当前 `PLAN_ID` 和 `PWF_PLAN_ROOT`。仅使用已存在的 `.planning/<PLAN_ID>/`；无法唯一确定计划时，请用户指定 `PLAN_ID`。
2. 将产物写入 `<PLAN_DIR>/artifacts/`。用户指定文件名时沿用；否则用简短主题命名，文本默认 `.md`，现有文件保留扩展名和原始字节。目标路径必须位于该目录内；同名时追加数字后缀，不覆盖已有文件。如果产物已在当前计划目录中，沿用原路径。
3. 在 `<PLAN_DIR>/progress.md` 记录产物路径和一句用途。确认保存后的内容与原产物一致，并向用户返回最终路径。
