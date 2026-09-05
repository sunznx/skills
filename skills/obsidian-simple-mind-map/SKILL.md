---
name: obsidian-simple-mind-map
description: 在 Obsidian 中创建、读取和增量编辑 Simple Mind Map 的 `.smm.md` 文件。用于 Markdown 转脑图、查询节点 UID、增加/改名/删除节点、设置外部链接或 Vault 内部文件引用，以及刷新预览图；不用于普通脑图图片或 XMind 文件。
---

# Obsidian Simple Mind Map

通过已安装的 `simple-mind-map` 插件操作 `.smm.md`，让插件负责数据规范化、压缩、索引和预览图生成。使用本 skill 目录中的 `scripts/smm_cli.py`；不要直接改 `.smm.md` 的 Base64 metadata。

## 前提

- Obsidian 正在运行，CLI 已启用。
- 目标 vault 已启用 `simple-mind-map` 插件。
- 默认 vault 名为 `obsidian`，默认根目录为 `/Users/sunx/Dropbox/syncer/apps/obsidian`；其他 vault 用 `--vault` 和 `--vault-root` 覆盖。

先探测接口：

```bash
python3 <skill-dir>/scripts/smm_cli.py probe
```

`probe` 只确认插件已加载及转换接口存在，不验证脑图视图的事件握手。若 CLI 无输出，串行重试一次并报告原始错误；不要据此断言 Obsidian 未运行。若 probe 报插件不可用，停止写入并报告插件版本。

## 工作流

### Markdown 转 `.smm.md`

临时 Markdown 必须已在 vault 中；转换成功或失败后都删除它，最终只保留新建的 `.smm.md`：

```bash
python3 <skill-dir>/scripts/smm_cli.py convert-md "notes/path/topic.md" --delete-source
```

只在输入是临时产物时使用 `--delete-source`；转换已有 Markdown 文档时省略该参数。不要自动选择插件的“覆盖转换”。新图的全部节点使用 Obsidian `textFontFamily`；未配置自定义字体时使用当前主题的 `--font-text`。返回值中的 `path` 是实际生成文件，文件重名时插件会自动改名。

### 读取与定位节点

```bash
python3 <skill-dir>/scripts/smm_cli.py read "notes/path/topic.smm.md"
```

节点文字可能重复；增量编辑必须使用 `uid`。用户只给文字时，先读取并展示所有匹配项；只有唯一匹配时才能继续。

### 增量编辑

```bash
python3 <skill-dir>/scripts/smm_cli.py add-child FILE PARENT_UID "新节点"
python3 <skill-dir>/scripts/smm_cli.py add-sibling FILE NODE_UID "同级节点"
python3 <skill-dir>/scripts/smm_cli.py set-text FILE NODE_UID "新文字"
python3 <skill-dir>/scripts/smm_cli.py set-link FILE NODE_UID URL "链接标题"
python3 <skill-dir>/scripts/smm_cli.py delete FILE NODE_UID
```

`set-link` 使用插件原生的 `SET_NODE_HYPERLINK` 命令，将目标写入节点数据的 `hyperlink` 和 `hyperlinkTitle` 字段；它不是把 Markdown 链接写进 `text`。

外部链接使用完整 URL 和普通标题：

```json
{
  "data": {
    "text": "<p>打开 Grafana：。</p>",
    "hyperlink": "http://127.0.0.1:3001",
    "hyperlinkTitle": "http://127.0.0.1:3001",
    "richText": true
  }
}
```

Vault 内部文件引用使用文件的 vault 相对路径作为 `URL` 参数，并用 Obsidian 内部链接作为标题：

```bash
python3 <skill-dir>/scripts/smm_cli.py set-link \
  "notes/工作/项目/待办事项.smm.md" NODE_UID \
  "notes/工作/项目/心得.md" "[[心得]]"
```

对应节点数据为：

```json
{
  "data": {
    "hyperlink": "notes/工作/项目/心得.md",
    "hyperlinkTitle": "[[心得]]",
    "richText": true
  }
}
```

插件会把这种非 Web 链接交给 Obsidian 打开，并支持悬停预览。每个节点只有一个 `hyperlink`；这是可点击引用，不会把目标文件内容嵌入节点。

这些操作调用插件原生命令，因此保留撤销历史并由插件生成新节点 UID。`delete` 拒绝删除根节点。修改默认更新预览图；仅在用户明确接受预览暂时过期时传 `--no-preview`。

所有打开脑图视图的 CLI 读写命令按 Vault 使用同一把进程文件锁串行执行；`probe` 和 `self-test` 不占锁。

完成后再次 `read`，确认目标节点、父子关系和返回的新 UID。一次请求包含多个独立修改时，逐项执行并在最后验证；不要通过 Markdown 全量重建来代替局部编辑，以免丢失节点样式、链接和位置。

### 保存和刷新预览

```bash
python3 <skill-dir>/scripts/smm_cli.py save FILE
```

## 边界

- 文件路径可用 vault 相对路径；绝对路径必须位于 `--vault-root` 内。
- `set-text` 写入普通文本。`delete` 支持删除既有自由节点；富文本、节点图片、自由节点的创建/移动、主题和布局暂不自动修改，需要这些操作时先检查插件接口再扩展脚本。
- 外部 URL 和 Vault 内部文件引用都使用 `set-link` 写入 `hyperlink` 元数据；不要把链接语法塞进 `text`。
- `read` 会输出 `hyperlink`、`hyperlinkTitle`、`richText`，增量设置链接后必须重新 `read` 验证这三个字段。
- mutation 失败时报告原始错误。脚本只通过插件保存，不自行序列化 `.smm.md`。
- 临时 Markdown 使用 `convert-md --delete-source`，无论转换结果如何都清理；完成后确认只留下 `.smm.md`。
- 本接入基于插件 `0.2.7` 已确认的事件：`execCommand`、`getMindMapCurrentData`、`saveToLocal`，并在每次操作前做能力探测。
