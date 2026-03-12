# repo2nlm

[中文](README.md) | [English](README.en.md)

把 GitHub 仓库转换为 NotebookLM 结构化学习材料，输出：

- `RepoBook/`（代码与文档正文）
- `GraphBook.md`（目录职责 + import 关系）
- `manifest.json`（文件索引）
- `graph.json`（依赖图数据）
- `stats.json`（统计与增量变更）

## 给 AI Agent 安装

可以直接把这句话发给你的 AI agent：

```text
帮我安装 repo2nlm：https://raw.githubusercontent.com/bilppppp/Repo2NotebookLM-/main/install.md
```

安装说明文档：[`install.md`](install.md)

## 环境准备（venv）

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
# NotebookLM 非官方 API/CLI
pip install git+https://github.com/teng-lin/notebooklm-py.git
```

> notebooklm-py: https://github.com/teng-lin/notebooklm-py?tab=readme-ov-file

## 用法

```bash
repo2nlm ingest <repo_url> --branch main --out ./out --max-file-kb 200 \
  --exclude "node_modules/**,dist/**,.git/**"

repo2nlm update <repo_url> --out ./out

repo2nlm upload ./out --notebook <name_or_id> --create-if-missing
# 完整刷新远端同名 source（避免保留旧内容）
repo2nlm upload ./out --notebook <name_or_id> --replace-existing

# 把多个仓库输出合并上传到同一个 notebook
# 会自动把远端 source 标题改成 <repo>__<filename>.md 以避免冲突
# 同时会生成一个 WorkspaceIndex.md，便于跨 repo 导航和对比
repo2nlm upload ./out-mlflow ./out-dispatch ./out-hermes-agent \
  --notebook <name_or_id> --create-if-missing
```

## 说明

- `update` 会读取旧 `manifest.json` 计算变更文件，并重建输出。
- `upload` 依赖 `notebooklm` CLI（由 `notebooklm-py` 安装提供）。
- 如果希望 NotebookLM 中内容与本地 `out/` 严格一致，使用 `--replace-existing` 强制替换同名 source。
- `upload` 支持一次传入多个 `out-*` 目录；当目录数量大于 1 时，会自动使用 `out-` 后缀作为 repo 命名空间，把上传标题写成 `<repo>__<filename>.md`，避免不同 repo 的 `00_overview.md` / `GraphBook.md` 互相覆盖。
- 多目录上传时还会额外生成一个 `WorkspaceIndex.md`，汇总 repo 元信息、GraphBook 入口和跨 repo 提问建议。
- 对超大仓库会自动切换为分批上传+分批等待（无须额外参数），减少超长上传过程中的遗漏风险。

## 上传后是否保留本地 out 目录

建议按“审计优先、正文可再生”保留：

- 建议保留（体积小，便于追溯）：
  - `stats.json`（本次 commit、扫描统计）
  - `upload_map.json`（远端 source 对账结果，`missing_titles` 必须为空）
  - `manifest.json` / `graph.json`（可选，做后续 diff 或结构分析）
- 可删除（体积大，可重新生成）：
  - `RepoBook/*.md`
  - `GraphBook.md` / `GraphBook.part*.md`
  - `artifacts/`、截图、临时调试输出

清理示例（仅保留最小审计文件）：

```bash
bash skills/repo2notebooklm/scripts/cleanup_out.sh ./out-<name> --audit-only
```

## Skills（根目录）

- `skills/repo2notebooklm`: 把 Git 仓库转换为 RepoBook + GraphBook，并上传 NotebookLM。
- `skills/notebooklm-py`: 使用 `notebooklm` CLI 执行 Notebook/Source/Chat/Artifact/Research 全流程。
