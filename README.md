# Vivo 云盘下载工具

一个基于 Python 的异步 Vivo 云盘（Vivo 云服务）文件下载工具，支持自动创建目录和递归下载整个目录中的文件。

## ✨ 功能特性

- 🚀 异步并发下载，提升下载效率
- 📁 支持递归遍历目录结构
- 🔄 断点续传（自动跳过已下载文件）
- 📊 实时下载进度显示
- 🎯 保持原始目录结构

## 📦 安装

### 方式一：使用 pip

1. 克隆仓库：

```bash
git clone https://github.com/fxaxg/vivo-disk-download.git
cd vivo-disk-download
```

2. 安装依赖：

```bash
pip install httpx
```

### 方式二：使用 Poetry（推荐）

1. 克隆仓库：

```bash
git clone https://github.com/fxaxg/vivo-disk-download.git
cd vivo-disk-download
```

2. 安装 Poetry（如果尚未安装）：

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. 使用 Poetry 安装依赖：

```bash
poetry install
```

4. 激活虚拟环境：

```bash
poetry shell
```

## 🚀 获取 Cookie

要使用此工具，您需要从 Vivo 云盘获取 Cookie。请按照以下步骤操作：

1. 打开浏览器并访问 [Vivo 云盘个人中心](https://yun.vivo.com.cn/)。
2. 登录到您的账户。
3. 按下 `F12` 或右键点击页面并选择“检查”以打开开发者工具。
4. 导航到“网络”选项卡。
5. 点击页面上的“云盘”以加载相关请求。
6. 在“网络”选项卡中，找到 Fetch/XHR 请求： `metaListByDir.do` 。
7. 点击该请求并查看请求头。
8. 找到并复制请求头中完整的的 `Cookie` 部分。
9. 将复制的 Cookie 粘贴到项目根目录的 `config.py` 文件中：

   ```python
   # config.py
   COOKIES = "your_cookies_here"  # 将此处替换为您复制的 Cookie
   ```

通过这些步骤，您将能够成功获取并配置所需的 Cookie，以便使用 Vivo 云盘下载工具。

## 🚀 使用方法

1. 配置好 `config.py` 后，直接运行：

```bash
python main.py
```

2. 程序会自动：
   - 获取 STS 令牌
   - 遍历并显示目录结构
   - 开始并发下载文件
   - 保持原始目录结构存储到 `download` 文件夹

## ⚡️ 自定义配置

可以在 `main.py` 中调整以下参数：

- `max_concurrent_downloads`：最大并发下载数（默认为 3）
- `chunk_size`：下载块大小（默认为 8192 字节）

## 📝 注意事项

- 需要先登录 Vivo 云盘网页版获取 Cookie
- 下载文件将保存在程序目录下的 `download` 文件夹中
- 请确保磁盘有足够的存储空间

## 🔑 许可证

[MIT License](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！