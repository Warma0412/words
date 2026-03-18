# 歧义侦探 - 句法透视仪

一个基于Flask的双视角句法分析工具，可以同时展示句子的依存句法和成分句法。

## 功能特点

- **双视角分析**: 同时展示依存句法和成分句法
- **核心论元提取**: 自动提取主语、宾语等核心论元
- **歧义分析**: 专门针对经典歧义句子的分析提示
- **自动安装**: 首次运行自动安装依赖和下载语言模型
- **Web界面**: 美观的Web界面，无需安装额外软件
- **双语支持**: 支持中文和英文句子分析
- **文档上传**: 支持 .txt, .pdf, .docx 文件上传分析

## 在线演示

访问部署在云端的演示版本：[待部署后填写]

## 本地运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 下载语言模型

首次运行时会自动下载，也可以手动下载：

```bash
# 下载spaCy模型
python -m spacy download en_core_web_sm
python -m spacy download zh_core_web_sm

# 下载nltk数据
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger')"
```

### 运行应用

```bash
python app.py
```

访问: http://localhost:5000

---

## 🚀 免费部署指南

### 方案一：Render（推荐）

**优点**: 完全免费、自动部署、支持Python

1. 注册 [Render](https://render.com) 账号
2. 连接你的 GitHub 仓库
3. 创建新的 Web Service
4. 配置：
   - **Build Command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -m spacy download zh_core_web_sm`
   - **Start Command**: `python app.py`
5. 部署完成后获得免费网址：`https://你的应用名.onrender.com`

---

### 方案二：Railway

**优点**: 简单易用、免费额度充足

1. 注册 [Railway](https://railway.app) 账号
2. 连接 GitHub 仓库
3. 选择 Python 项目
4. 自动部署，获得网址：`https://你的应用名.up.railway.app`

---

### 方案三：PythonAnywhere

**优点**: 专门为Python设计

1. 注册 [PythonAnywhere](https://www.pythonanywhere.com) 免费账号
2. 上传代码文件
3. 创建 Web App
4. 配置 WSGI 文件
5. 获得网址：`https://你的用户名.pythonanywhere.com`

---

### 方案四：GitHub Pages + 静态化

**注意**: 仅适合静态网页，此项目需要后端，不推荐

---

## 📦 GitHub 上传步骤

### 1. 初始化 Git 仓库

```bash
cd "d:\【代码】\【Python】\机器学习\歧义侦探"
git init
git add .
git commit -m "初始提交: 歧义侦探句法分析工具"
```

### 2. 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击 "New repository"
3. 仓库名: `syntax-analyzer` 或 `歧义侦探`
4. 选择 Public
5. 点击 "Create repository"

### 3. 推送代码

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

---

## 项目结构

```
歧义侦探/
├── app.py                 # Flask后端应用
├── requirements.txt       # 依赖列表
├── runtime.txt           # Python版本
├── Procfile              # 部署配置
├── .gitignore            # Git忽略文件
├── 启动.bat              # Windows启动脚本
├── README.md             # 说明文档
├── templates/
│   └── index.html        # 主页面模板
└── static/
    ├── style.css         # 样式文件
    └── script.js         # JavaScript逻辑
```

---

## 技术栈

- **Flask**: Web应用框架
- **spaCy**: 依存句法分析
- **NLTK**: 成分句法分析
- **displaCy**: 依存关系可视化
- **HTML/CSS/JavaScript**: 前端界面

---

## 常见问题

### 问题1：模型下载失败
**解决方案**：手动下载模型
```bash
python -m spacy download en_core_web_sm
python -m spacy download zh_core_web_sm
```

### 问题2：端口被占用
**解决方案**：修改端口号
```python
app.run(debug=False, host='0.0.0.0', port=5001)
```

---

## License

MIT License
