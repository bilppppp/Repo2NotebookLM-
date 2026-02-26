# repo2nlm

把 GitHub 仓库转换为 NotebookLM 结构化学习材料，输出：

- `RepoBook/`（代码与文档正文）
- `GraphBook.md`（目录职责 + import 关系）
- `manifest.json`（文件索引）
- `graph.json`（依赖图数据）
- `stats.json`（统计与增量变更）

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
```

## 说明

- `update` 会读取旧 `manifest.json` 计算变更文件，并重建输出。
- `upload` 依赖 `notebooklm` CLI（由 `notebooklm-py` 安装提供）。

## Skills（根目录）

- `skills/repo2notebooklm`: 把 Git 仓库转换为 RepoBook + GraphBook，并上传 NotebookLM。
- `skills/notebooklm-py`: 使用 `notebooklm` CLI 执行 Notebook/Source/Chat/Artifact/Research 全流程。
