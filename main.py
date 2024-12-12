import httpx
import asyncio
from config import COOKIES, COMMON_HEADERS
import os
def extract_csrftoken_from_cookie(cookie: str) -> str:
    """从 cookie 中提取 vivo_yun_csrftoken 的值"""
    cookie_pairs = cookie.split(';')
    for pair in cookie_pairs:
        if 'vivo_yun_csrftoken' in pair:
            return pair.split('=')[1].strip()
    return ''

def get_headers(variables: dict = None) -> dict:
    """构建请求头，支持变量替换"""
    headers = COMMON_HEADERS.copy()
    
    if variables is None:
        variables = {}
    
    # 获取默认 cookie
    cookie = variables.get('cookie', COOKIES)
    # 从 cookie 中提取 csrftoken
    csrftoken = extract_csrftoken_from_cookie(cookie)
    
    # 设置默认变量
    default_vars = {
        'cookie': cookie,
        'csrftoken': csrftoken
    }
    
    # 合并用户提供的变量
    variables = {**default_vars, **variables}
    
    # 替换模板变量
    for key, value in headers.items():
        if isinstance(value, str):
            headers[key] = value.format(**variables)
    
    return headers

async def get_sts_token() -> dict:
    url = "https://clouddisk-api.vivo.com.cn/api/webdisk/user/getStsToken.do?tokenType=2&_t=1733980240737"
    headers = get_headers()  # 使用默认变量
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()
    
async def get_meta_list_by_dir(sys_token: str, dir_id: str = ""):
    url = f"https://clouddisk-api.vivo.com.cn/api/webdisk/meta/metaListByDir.do?sysToken={sys_token}&dirId={dir_id}&pageSize=10000&preName=&preIsDir=&_t=1733980240737"
    headers = get_headers()  # 使用默认变量
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

async def traverse_directory(sts_token: str, dir_id: str = "", level: int = 0):
    """
    递归遍历目录结构并返回所有文件信息
    
    Args:
        sts_token: STS 令牌
        dir_id: 目录 ID
        level: 当前递归层级，用于控制缩进
    Returns:
        list: 包含所有文件和目录信息的列表
    """
    result = []
    meta_list = await get_meta_list_by_dir(sts_token, dir_id)
    
    if not meta_list.get('data') or not meta_list['data'].get('metaList'):
        return result
    
    for item in meta_list['data']['metaList']:
        item['level'] = level  # 添加层级信息
        result.append(item)
        
        if item['dir']:
            children = await traverse_directory(sts_token, item['metaId'], level + 1)
            result.extend(children)
    
    return result

async def download_file(file_info: dict, sts_token: str, semaphore: asyncio.Semaphore):
    """
    下载单个文件
    
    Args:
        file_info: 文件信息字典
        sts_token: STS 令牌
        semaphore: 异步信号量，用于控制并发
    """
    file_name = file_info['fileName']
    file_path = file_info['absolutePath']
    meta_id = file_info['metaId']
    
    # 构建下载路径
    download_dir = os.path.join("download", os.path.dirname(file_path.lstrip('/')))
    download_path = os.path.join(download_dir, file_name)
    
    # 检查文件是否已存在
    if os.path.exists(download_path):
        print(f"文件已存在，跳过下载: {download_path}")
        return
    
    # 确保目录存在
    os.makedirs(download_dir, exist_ok=True)
    
    file_url = f"https://clouddisk-cn09.vivo.com.cn/api/file/webdisk/download.do?stsToken={sts_token}&metaId={meta_id}"
    
    async with semaphore:
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream('GET', file_url) as response:
                    response.raise_for_status()
                    total_size = int(response.headers.get('content-length', 0))
                    
                    with open(download_path, 'wb') as f:
                        downloaded = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            # 显示下载进度
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                print(f"\r下载进度 {file_name}: {progress:.1f}%", end='', flush=True)
                        
                        print(f"\n完成下载: {download_path}")
        except Exception as e:
            print(f"下载文件 {file_name} 失败: {str(e)}")
            # 如果下载失败，删除可能部分下载的文件
            if os.path.exists(download_path):
                os.remove(download_path)
            raise

async def process_directory_structure(all_files: list):
    """处理目录结构"""
    for file in all_files:
        indent = "    " * file['level']
        print(f"{indent}{file['fileName']}")
        if file['dir']:
            download_path = os.path.join("download", file['absolutePath'].lstrip('/'))
            os.makedirs(download_path, exist_ok=True)

async def download_all_files(all_files: list, sts_token: str, max_concurrent_downloads: int = 3):
    """
    下载所有文件
    
    Args:
        all_files: 文件信息列表
        sts_token: STS 令牌
        max_concurrent_downloads: 最大并发下载数
    """
    # 创建信号量控制并发
    semaphore = asyncio.Semaphore(max_concurrent_downloads)
    
    # 过滤出非目录文件
    files_to_download = [f for f in all_files if not f['dir']]
    
    # 创建下载任务
    tasks = [download_file(f, sts_token, semaphore) for f in files_to_download]
    
    # 并发执行下载任务
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"下载过程中发生错误: {str(e)}")

async def main():
    try:
        # 获取 STS 令牌
        sts_response = await get_sts_token()
        sts_token = sts_response['data']['stsToken']
        
        # 获取所有文件信息
        all_files = await traverse_directory(sts_token)
        
        # 处理目录结构
        await process_directory_structure(all_files)
        
        # 下载所有文件
        await download_all_files(all_files, sts_token)
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())