# 命运回响 · 本地前后端版说明

这个版本是在原 Python 版基础上新增的完整本地运行项目。

## 它解决什么问题

原来的 Streamlit 版适合快速做文本原型，纯网页离线版适合没有环境配置能力的用户直接打开。  
本地前后端版介于两者之间：

- 前端是浏览器网页
- 后端是 Python FastAPI
- 剧情、随机事件和大模型调用都放在后端
- API Key 不直接写进前端 JS
- 适合继续开发成更成熟的本地产品

## 怎么启动

双击：

```text
一键启动前后端版.bat
```

启动后打开：

```text
http://127.0.0.1:8787
```

## 主要功能

- 开局选择人设模板
- 自定义人设
- 不同随机性强度
- 每章随机状态事件
- 本地动态选项
- AI 优化人设
- AI 生成额外选择
- 完整终局报告

## AI 怎么配置

进入页面右上角 `AI 设置`。

DeepSeek 可用：

```text
接口地址：https://api.deepseek.com/chat/completions
模型：deepseek-chat
```

填入自己的 API Key 后点击保存。

配置会保存到：

```text
life_sim_data/ai_config.json
```

注意：

- 不要把带真实 Key 的 `ai_config.json` 发给别人。
- 如果 AI 返回 HTTP 402，通常是 API 余额不足。
- 如果要做线上公开服务，应使用后端权限和用户体系，不应开放任意本地配置接口。

## 文件说明

```text
api_server.py                 # FastAPI 后端
fullstack_web/index.html      # 前端入口
fullstack_web/style.css       # 前端样式
fullstack_web/app.js          # 前端交互逻辑
一键启动前后端版.bat            # 推荐启动入口
```
