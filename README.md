# RustDesk Auto Deployment Tool (Enterprise Edition)

这是一个基于 Python 开发的企业级 RustDesk 自动部署工具。它能够实现静默安装、自动配置自建服务器信息、以及自动登记客户端资产信息到共享 CSV 文件。

## ✨ 功能特性 (Features)

* **静默安装**: 自动检测环境并静默安装 RustDesk 客户端。
* **自动配置**: 自动下发自建服务器的 Host IP 和 Key 配置。
* **资产登记**: 自动获取本机的主机名、内网 IP 和 RustDesk ID，并写入网络共享的 CSV 文件。
* **信息隐蔽**: 运行时不显示具体的网络共享路径，保护内网架构信息。
* **UAC 提权**: 自动请求管理员权限以执行安装操作。

## 🛠️ 环境依赖 (Requirements)

* Windows 10 / 11
* Python 3.x (仅编译时需要)
* 依赖库: 标准库 (`os`, `subprocess`, `socket`, `csv`, `shutil`)

## 🚀 使用指南 (Usage)

1.  **修改配置**: 打开脚本 `script_rustdesk.py`，修改顶部的配置区域：
    ```python
    SHARE_ROOT = r"\\YOUR_NAS\Share"  # 你的共享目录
    SERVER_IP = "192.168.1.x"         # 你的 RustDesk 服务器 IP
    SERVER_KEY = "..."                # 你的服务器公钥
    ```
2.  **打包**: 使用 PyInstaller 将脚本打包为 exe 文件：
    ```bash
    pyinstaller --onefile --uac-admin --icon="logo.ico" script_rustdesk.py
    ```
3.  **部署**: 将生成的 `.exe` 文件和 `rustdesk.exe` 安装包放入配置好的共享目录中。

## 📝 资产登记格式

程序会自动在共享目录生成 `RustDesk_Client_List.csv`，格式如下：

| 登记时间 | 电脑名称 | IP地址 | RustDesk ID |
| :--- | :--- | :--- | :--- |
| 2025-12-15 09:00:00 | WORK-PC-01 | 192.168.5.10 | 123456789 |

## ⚖️ License

MIT License