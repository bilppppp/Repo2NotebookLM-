# AGENTS.md

本文件用于给后续 AI/Agent 协作者快速提供项目上下文（类似 `CLAUDE.md` 的用途）。

## 项目目标

将 GitHub Repo 转成 NotebookLM 友好的结构化学习材料：

- RepoBook（代码正文与目录结构）
- GraphBook（目录职责与依赖关系）

## 快速开始

```bash
cd "/Users/gravity/Desktop/AI/Repo 到NotebookLM "
. .venv/bin/activate
./repo2nlm --help
```

## 常用命令

```bash
./repo2nlm ingest <repo_url> --branch main --out ./out --max-file-kb 200
./repo2nlm update <repo_url> --out ./out
./repo2nlm upload ./out --notebook <name_or_id> --create-if-missing
```

## 代码结构

- `src/repo2nlm/cli.py`：命令行入口
- `src/repo2nlm/git_ops.py`：仓库克隆与 commit 定位
- `src/repo2nlm/scanner.py`：文件扫描、过滤、文本/二进制判断
- `src/repo2nlm/graph_builder.py`：入口检测、import 图谱、目录职责
- `src/repo2nlm/renderers/books.py`：RepoBook/GraphBook/JSON 渲染
- `src/repo2nlm/uploader.py`：NotebookLM 上传适配

## 注意事项

- `upload` 依赖 `notebooklm` CLI（由 `notebooklm-py` 提供）
- 当前实现覆盖 MVP（Phase0 + Phase1），已完成真实仓库端到端验证
- 若继续做 Phase2/Phase3，优先扩展 `graph_builder.py`

## 当前验证结论

- `nanochat` 全流程已跑通：`ingest -> upload -> ask -> generate/download artifacts`
- NotebookLM 关键能力已验证：`source` / `chat` / `artifact` / `note` / `research` / `share` / `language`
- 验证输出目录：`out-nanochat/`（含 `artifacts/`）

## 快速复用流程（下一个仓库）

```bash
cd "/Users/gravity/Desktop/AI/Repo 到NotebookLM "
. .venv/bin/activate
./repo2nlm ingest <repo_url> --out ./out-<name>
./repo2nlm upload ./out-<name> --notebook "<name_or_id>" --create-if-missing
```
