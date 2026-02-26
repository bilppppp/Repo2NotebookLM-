# Repo2NLM 工作记录

更新时间：2026-02-26

## 已完成

- 根据需求文档实现 `repo2nlm` MVP（Phase0 + Phase1）
- 实现 CLI 子命令：`ingest` / `update` / `upload`
- 输出产物：
  - `RepoBook/*.md`
  - `GraphBook.md`
  - `manifest.json`
  - `graph.json`
  - `stats.json`
- 实现仓库抓取与快照：支持 `repo_url` + `branch/commit`
- 实现过滤与内容策略：默认排除目录、二进制识别、超大文件截断
- 实现 Import Graph（Python + JS/TS）：
  - Python: `import` / `from ... import ...`
  - JS/TS: `import from` / `require()` / `import()`（静态字符串）
  - internal/external 区分 + evidence（行号/片段）
- 实现目录职责推断与入口检测
- 实现增量更新比对：基于 `manifest.json` 产出 `changed_files/deleted_files`
- 创建 `venv`：`.venv`
- 安装并验证 `notebooklm-py`（`notebooklm` CLI 可用）
- 编写项目说明与协作文档：`README.md` / `AGENTS.md`
- 本地样例仓库完成端到端冒烟验证（`ingest` + `update`）
- 对 `https://github.com/karpathy/nanochat` 完成真实端到端验证：
  - `ingest` 生成 `out-nanochat/` 全量产物
  - `upload` 成功上传 RepoBook + GraphBook 到 NotebookLM
  - `ask` 问答成功并保存 JSON（含引用）
  - 产物生成与下载成功：`report` / `mind-map` / `data-table` / `infographic` / `audio` / `slide-deck` / `quiz` / `flashcards` / `video`
  - `artifact export` 成功导出 Google Docs
  - `source add/rename/wait/delete`、`research status/wait --import-all`、`note create/get/save/rename/delete` 已验证

## 当前状态

- 项目开发与验证已完成，可直接用于下一个仓库
- 当前实现覆盖 PRD 的 MVP 目标（Phase0 + Phase1）
- Phase2/Phase3（符号级索引 / call graph）尚未实现

## 已验证输出位置

- `out-nanochat/RepoBook/*.md`
- `out-nanochat/GraphBook.md`
- `out-nanochat/manifest.json`
- `out-nanochat/graph.json`
- `out-nanochat/stats.json`
- `out-nanochat/ask-architecture.json`
- `out-nanochat/artifacts/*`（下载产物）

## 关键文件

- `src/repo2nlm/cli.py`
- `src/repo2nlm/graph_builder.py`
- `src/repo2nlm/scanner.py`
- `src/repo2nlm/renderers/books.py`
- `src/repo2nlm/uploader.py`
- `repo2nlm`（本地运行入口）
