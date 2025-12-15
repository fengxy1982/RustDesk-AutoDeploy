import os
import subprocess
import socket
import csv
import time
import shutil
import sys

# ================= 必须配置区域 (Configuration) =================

# 1. 共享目录根路径 / Shared Directory
# 请修改为你实际的内网共享路径
SHARE_ROOT = r"\\YOUR_FILE_SERVER\Rustdesk_Share"

# 2. 具体文件路径
NETWORK_INSTALLER_PATH = os.path.join(SHARE_ROOT, "rustdesk.exe")
CSV_PATH = os.path.join(SHARE_ROOT, "RustDesk_Client_List.csv")

# 3. 本地临时路径
LOCAL_TEMP_PATH = os.path.join(os.environ["TEMP"], "rd_setup.exe")

# 4. RustDesk 主程序路径
RUSTDESK_EXE = r"C:\Program Files\RustDesk\rustdesk.exe"

# 5. 自建服务器配置 / Self-hosted Server Config
# 【重要】请填入你的公钥 / Please fill in your public key
SERVER_IP = "YOUR_SERVER_IP_OR_DOMAIN"
SERVER_KEY = "YOUR_PUBLIC_KEY_HERE" 
CONFIG_STRING = f"host={SERVER_IP},key={SERVER_KEY}"

# ==============================================================

def run_command(command):
    """运行系统命令并返回输出"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    except:
        return None

def download_installer():
    """从共享目录静默下载"""
    print("正在连接服务器获取组件...") # 模糊提示
    
    if not os.path.exists(NETWORK_INSTALLER_PATH):
        print("错误：无法连接部署服务器，请联系IT部门。") # 不显示具体路径
        return False
    
    try:
        shutil.copy2(NETWORK_INSTALLER_PATH, LOCAL_TEMP_PATH)
        # print("下载完成") # 保持安静
        return True
    except Exception:
        print("组件获取失败。")
        return False

def install_rustdesk():
    """安装 RustDesk"""
    if os.path.exists(RUSTDESK_EXE):
        print("检测到客户端已存在，准备进行配置更新...")
        return True
    
    if not download_installer():
        return False

    print("正在安装远程协助组件，请稍候...")
    cmd = f'"{LOCAL_TEMP_PATH}" --silent-install'
    subprocess.run(cmd, shell=True)
    
    print("正在启动服务 (需等待约10秒)...")
    time.sleep(10) 
    
    # 清理临时文件
    try:
        if os.path.exists(LOCAL_TEMP_PATH):
            os.remove(LOCAL_TEMP_PATH)
    except:
        pass

    if os.path.exists(RUSTDESK_EXE):
        print("组件安装成功。")
        return True
    else:
        print("安装未成功，请手动联系IT支持。")
        return False

def set_config():
    """设置 ID 服务器和 Key"""
    print("正在应用安全策略...") # 模糊提示
    if os.path.exists(RUSTDESK_EXE):
        cmd = f'"{RUSTDESK_EXE}" --config "{CONFIG_STRING}"'
        subprocess.run(cmd, shell=True)
        time.sleep(2)
    else:
        print("配置失败：找不到主程序。")

def get_rustdesk_id():
    """获取 RustDesk ID"""
    print("正在验证客户端 ID...")
    
    if not os.path.exists(RUSTDESK_EXE):
        return "Not Installed"

    for i in range(5):
        cmd = f'"{RUSTDESK_EXE}" --get-id'
        rid = run_command(cmd)
        
        if rid and " " not in rid and len(rid) > 6:
            return rid
        
        time.sleep(3)
    
    return "Get Failed"

def get_local_info():
    """获取本机主机名和IP"""
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = socket.gethostbyname(hostname)
    return hostname, ip

def write_to_csv(hostname, ip, rustdesk_id):
    """写入信息到网络共享 CSV"""
    print("正在登记资产信息...")
    
    # 简单的权限检查，不报错给用户
    try:
        file_exists = os.path.exists(CSV_PATH)
        
        with open(CSV_PATH, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["登记时间", "电脑名称", "IP地址", "RustDesk ID"])
            
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writer.writerow([current_time, hostname, ip, rustdesk_id])
            print("信息登记完成。")
            return True
    except PermissionError:
        print("登记失败：服务器访问被拒绝。") # 不显示路径
    except Exception:
        print("登记失败：网络写入错误。") # 不显示路径
    return False

def main():
    print("=== 亚世光电 信息办 RustDesk 部署工具 By 冯工 ===")
    print("初始化中...")
    
    # 1. 安装
    if not install_rustdesk():
        return

    # 2. 配置
    set_config()

    # 3. 获取信息
    rust_id = get_rustdesk_id()
    hostname, ip = get_local_info()
    
    # 只显示结果，不显示过程路径
    print("-" * 30)
    print(f"电脑名称: {hostname}")
    print(f"IP 地址 : {ip}")
    print(f"远程 ID : {rust_id}")
    print("-" * 30)

    # 4. 回写
    if rust_id != "Get Failed" and rust_id != "Not Installed":
        write_to_csv(hostname, ip, rust_id)
    else:
        print("ID 获取异常，跳过登记。")

if __name__ == "__main__":
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if is_admin:
        try:
            main()
        except Exception:
            # 捕获所有未预料的错误，防止爆出 traceback 暴露代码路径
            print("运行过程中发生未知错误。")
        
        print("\n部署结束。")
        input("按回车键退出窗口...") 
    else:
        print("权限不足：请右键点击本程序，选择【以管理员身份运行】。")
        input("按回车键退出...")