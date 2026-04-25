# 命运回响

一个基于 Streamlit 的互动式现实人生模拟工具。用户会从小学、初中、高考、大学走到初入社会，在关键节点做选择，最终生成需求、受伤线索、决策风格和结局报告。

## 给普通用户：最少操作运行

双击 `一键启动.bat`。

首次运行会自动创建 `.venv` 本地环境并安装依赖。之后再次双击会直接启动。浏览器会打开 `http://localhost:8501`。

如果提示未检测到 Python，请先看 `安装说明.md`。

## 给完全不想配置环境的用户

如果你希望对方电脑上不安装 Python、不打开命令行、不手动安装依赖，请先在你自己的电脑上双击：

`一键打包EXE.bat`

打包完成后，把 `dist\命运回响` 整个文件夹发给对方。对方打开该文件夹里的 `命运回响.exe` 即可启动。

注意：Streamlit 是本地网页应用，exe 启动后仍会打开浏览器页面，这是正常行为。

## 给分发者

如果对方电脑有 Python，把整个文件夹发给对方即可，至少包含：

- `app.py`
- `requirements.txt`
- `一键启动.bat`
- `launcher.py`
- `life_echo.py`
- `README.md`
- `安装说明.md`

不建议只发单个 `app.py`，因为普通用户需要启动脚本和依赖说明。

## 给开发者

运行：

```powershell
pip install -r requirements.txt
streamlit run app.py
```

作为模块复用：

```python
import life_echo

state = life_echo.create_initial_state()
node = life_echo.get_current_node(state)
choices = life_echo.get_available_choices(node, state)
state = life_echo.choose(state, choices[0][0])
```

## 数据保存

存档默认写入项目目录下的 `life_sim_data`。如果目录不可写，会自动保存到用户目录下的 `.life_sim_data`。

## 产品边界

本项目是互动叙事和自我觉察工具，不提供医学诊断、心理疾病判断、危机干预
