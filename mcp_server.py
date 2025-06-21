from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import os
import subprocess
import shutil
import platform
import socket
import requests
import zipfile
import glob
import asyncio
from playwright.async_api import async_playwright
import math
import datetime
import time
import difflib

# Environment-based configuration
HOST = os.getenv("MCP_HOST", "0.0.0.0")  # Use 0.0.0.0 for container deployment
PORT = int(os.getenv("MCP_PORT", "8000"))
PATH = os.getenv("MCP_PATH", "/mcp")
WORKSPACE_DIR = os.getenv("MCP_WORKSPACE", "/app/workspace")
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

mcp = FastMCP("Local MCP Server")

# Singleton for Playwright browser
_playwright = None
_browser = None

async def get_browser():
    global _playwright, _browser
    if _playwright is None:
        _playwright = await async_playwright().start()
    if _browser is None:
        _browser = await _playwright.chromium.launch(headless=BROWSER_HEADLESS)
    return _browser

@mcp.tool()
def list_dir(base_dir: str, path: str = ".") -> List[str]:
    """
    List all files and folders in a directory under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir to list (default is "." for the base directory itself).
    
    Returns:
        List[str]: A list of file and folder names in the specified directory.
    
    Use case: To enumerate the contents of a project or subfolder, e.g., to find available files to read or edit.
    """
    abs_path = os.path.join(base_dir, path)
    return os.listdir(abs_path)

@mcp.tool()
def read_file(base_dir: str, path: str) -> str:
    """
    Read the contents of a text file under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir to the file to read.
    
    Returns:
        str: The contents of the file as a string.
    
    Use case: To view or process the contents of a file, such as source code, configuration, or documentation.
    """
    abs_path = os.path.join(base_dir, path)
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()

@mcp.tool()
def write_file(base_dir: str, path: str, content: str) -> None:
    """
    Write content to a file (overwriting if it exists) under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir to the file to write.
        content (str): The text content to write to the file.
    
    Returns:
        None
    
    Use case: To create or update files, such as saving code, notes, or configuration changes.
    """
    abs_path = os.path.join(base_dir, path)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)

@mcp.tool()
def delete_file(base_dir: str, path: str) -> None:
    """
    Delete a file under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir to the file to delete.
    
    Returns:
        None
    
    Use case: To remove unwanted or obsolete files from a project or workspace.
    """
    abs_path = os.path.join(base_dir, path)
    os.remove(abs_path)

@mcp.tool()
def create_folder(base_dir: str, path: str) -> None:
    """
    Create a new folder under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir for the new folder to create.
    
    Returns:
        None
    
    Use case: To organize files by creating new directories for code, data, or other resources.
    """
    abs_path = os.path.join(base_dir, path)
    os.makedirs(abs_path, exist_ok=True)

@mcp.tool()
def delete_folder(base_dir: str, path: str) -> None:
    """
    Delete a folder and all its contents under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir to the folder to delete.
    
    Returns:
        None
    
    Use case: To remove entire directories, such as cleaning up temporary or obsolete project folders.
    """
    abs_path = os.path.join(base_dir, path)
    shutil.rmtree(abs_path)

@mcp.tool()
def execute_shell_command(command: str, base_dir: str, cwd: str = None) -> Dict[str, Any]:
    """
    Execute a shell command in a specified working directory under a base directory and return the output.
    Prevents execution of dangerous commands that could harm the container or host.
    """
    # Blacklist of dangerous commands/patterns
    blacklist = [
        'rm -rf', 'rm -r /', 'rm -rf /', 'shutdown', 'reboot', 'poweroff', 'halt',
        'mkfs', 'dd ', ':(){:|:&}', '>:(', 'kill 1', 'kill -9 1', 'killall', 'init 0',
        'init 6', 'systemctl', 'chown /', 'chmod 000 /', 'mv /', 'cp /dev/zero',
        '>/dev/sda', '>/dev/vda', '>/dev/hda', '>/dev/nvme', '>/dev/xvda', '>/dev/mmcblk',
        '>/dev/sdb', '>/dev/sdc', '>/dev/sdd', '>/dev/sde', '>/dev/sdf', '>/dev/sdg',
        '>/dev/sdh', '>/dev/sdi', '>/dev/sdj', '>/dev/sdk', '>/dev/sdl', '>/dev/sdm',
        '>/dev/sdn', '>/dev/sdo', '>/dev/sdp', '>/dev/sdq', '>/dev/sdr', '>/dev/sds',
        '>/dev/sdt', '>/dev/sdu', '>/dev/sdv', '>/dev/sdw', '>/dev/sdx', '>/dev/sdy',
        '>/dev/sdz', 'docker stop', 'docker kill', 'docker rm', 'docker rmi', 'docker system prune',
        'docker-compose down', 'docker-compose rm', 'docker-compose stop', 'docker-compose kill',
        'crontab -r', 'userdel', 'groupdel', 'passwd', 'su ', 'sudo ', 'visudo', 'adduser', 'addgroup',
        'deluser', 'delgroup', 'pkill', 'reboot', 'halt', 'poweroff', 'shutdown', 'init '
    ]
    lower_command = command.lower()
    for pattern in blacklist:
        if pattern in lower_command:
            return {
                "stdout": "",
                "stderr": f"Blocked dangerous command: '{pattern}' detected in input.",
                "returncode": 126
            }
    abs_cwd = os.path.join(base_dir, cwd) if cwd else base_dir
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=abs_cwd)
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

@mcp.tool()
def get_file_info(base_dir: str, path: str) -> Dict[str, Any]:
    """
    Get metadata for a file or folder under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str): The relative path from base_dir to the file or folder.
    
    Returns:
        Dict[str, Any]: A dictionary with file/folder metadata: path, is_file, is_dir, size, created, modified, mode.
    
    Use case: To inspect file properties, such as size, type, or modification time, for project management or validation.
    """
    abs_path = os.path.join(base_dir, path)
    stat = os.stat(abs_path)
    return {
        "path": abs_path,
        "is_file": os.path.isfile(abs_path),
        "is_dir": os.path.isdir(abs_path),
        "size": stat.st_size,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "mode": stat.st_mode
    }

@mcp.tool()
def search_files(base_dir: str, pattern: str, root: str = ".") -> List[str]:
    """
    Search for files by name pattern (glob) under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        pattern (str): The filename pattern to search for (e.g., '*.py' for Python files).
        root (str, optional): The relative path from base_dir to start the search (default is ".").
    
    Returns:
        List[str]: A list of matching file paths.
    
    Use case: To find files of a certain type or name, such as all Python scripts or README files in a project.
    """
    abs_root = os.path.join(base_dir, root)
    return glob.glob(os.path.join(abs_root, "**", pattern), recursive=True)

@mcp.tool()
def zip_files(base_dir: str, zip_path: str, files: List[str]) -> None:
    """
    Create a zip archive from a list of files under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        zip_path (str): The relative path from base_dir for the new zip file to create.
        files (List[str]): A list of relative file paths (from base_dir) to include in the archive.
    
    Returns:
        None
    
    Use case: To package multiple files for download, backup, or sharing.
    """
    abs_zip_path = os.path.join(base_dir, zip_path)
    with zipfile.ZipFile(abs_zip_path, 'w') as zipf:
        for file in files:
            abs_file = os.path.join(base_dir, file)
            zipf.write(abs_file, arcname=os.path.basename(abs_file))

@mcp.tool()
def unzip_file(base_dir: str, zip_path: str, extract_to: str) -> None:
    """
    Extract a zip archive to a directory under a specified base directory.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        zip_path (str): The relative path from base_dir to the zip file to extract.
        extract_to (str): The relative path from base_dir for the directory to extract files into.
    
    Returns:
        None
    
    Use case: To unpack downloaded or received zip files into a project workspace.
    """
    abs_zip_path = os.path.join(base_dir, zip_path)
    abs_extract_to = os.path.join(base_dir, extract_to)
    with zipfile.ZipFile(abs_zip_path, 'r') as zipf:
        zipf.extractall(abs_extract_to)

@mcp.tool()
def directory_tree(base_dir: str, path: str = ".", max_depth: int = 3) -> str:
    """
    Return a tree-like string representation of the directory structure under a specified base directory up to a given depth.
    
    Parameters:
        base_dir (str): The absolute path to the root directory the agent is allowed to access.
        path (str, optional): The relative path from base_dir to the directory to visualize (default is ".").
        max_depth (int, optional): The maximum depth of subdirectories to display (default is 3).
    
    Returns:
        str: A string representing the directory tree.
    
    Use case: To visualize the folder structure of a project or workspace for navigation or planning.
    """
    abs_path = os.path.join(base_dir, path)
    def tree(dir_path, prefix="", depth=0):
        if depth > max_depth:
            return ""
        entries = []
        try:
            entries = os.listdir(dir_path)
        except Exception:
            return prefix + "[Permission Denied]\n"
        result = ""
        for i, entry in enumerate(sorted(entries)):
            full_path = os.path.join(dir_path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            result += f"{prefix}{connector}{entry}\n"
            if os.path.isdir(full_path):
                extension = "    " if i == len(entries) - 1 else "│   "
                result += tree(full_path, prefix + extension, depth + 1)
        return result
    return f"{abs_path}\n" + tree(abs_path)

# The following tools are not directory-restricted and remain global
@mcp.tool()
def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information about the machine running the MCP server.
    
    Returns:
        Dict[str, Any]: A dictionary with OS, version, platform, CPU, hostname, current working directory, and disk usage.
    
    Use case: To gather environment details for debugging, reporting, or system checks.
    """
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "hostname": socket.gethostname(),
        "cwd": os.getcwd(),
        "disk_usage": shutil.disk_usage(os.getcwd())
    }

@mcp.tool()
def ping_host(host: str, count: int = 1) -> Dict[str, Any]:
    """
    Ping a remote host from the MCP server and return the results.
    
    Parameters:
        host (str): The hostname or IP address to ping.
        count (int, optional): The number of ping attempts to make (default is 1).
    
    Returns:
        Dict[str, Any]: A dictionary with 'stdout' (ping output), 'stderr' (errors), and 'returncode' (exit code).
    
    Use case: To check network connectivity or latency to a server or website from the MCP server's machine.
    """
    try:
        if platform.system().lower() == "windows":
            param = "-n"
        else:
            param = "-c"
        
        result = subprocess.run(["ping", param, str(count), host], capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Ping command timed out",
            "returncode": -1
        }
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": "Ping command not available in this environment",
            "returncode": -1
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

@mcp.tool()
def download_url(url: str, save_path: str) -> None:
    """
    Download a file from a URL and save it to a specified path on the MCP server.
    
    Parameters:
        url (str): The URL to download the file from.
        save_path (str): The absolute or relative path on the server to save the downloaded file.
    
    Returns:
        None
    
    Use case: To fetch resources, datasets, or code from the internet for use in a project or analysis.
    """
    r = requests.get(url)
    r.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(r.content)

@mcp.tool()
def list_processes() -> List[Dict[str, Any]]:
    """
    List all running processes on the MCP server's machine.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries with process names and PIDs.
    
    Use case: To monitor or manage running applications, or to find processes to terminate.
    """
    processes = []
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["tasklist"], capture_output=True, text=True)
            for line in result.stdout.splitlines()[3:]:
                parts = line.split()
                if parts:
                    processes.append({"name": parts[0], "pid": parts[1]})
        else:
            # Cross-platform approach using psutil
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        processes.append({
                            "name": proc.info['name'],
                            "pid": str(proc.info['pid'])
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except ImportError:
                # Fallback to ps command
                result = subprocess.run(["ps", "-eo", "pid,comm"], capture_output=True, text=True)
                for line in result.stdout.splitlines()[1:]:
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2:
                        processes.append({"pid": parts[0], "name": parts[1]})
    except Exception as e:
        processes.append({"error": str(e)})
    return processes

@mcp.tool()
def kill_process(pid: int) -> None:
    """
    Kill a running process on the MCP server by its process ID (PID).
    
    Parameters:
        pid (int): The process ID of the process to terminate.
    
    Returns:
        None
    
    Use case: To stop runaway or unwanted processes, or to manage system resources.
    """
    os.kill(pid, 9)

@mcp.tool()
def http_request_tool(method: str, url: str, headers: Optional[Dict[str, str]] = None, data: Optional[str] = None, json_data: Optional[dict] = None, timeout: int = 10) -> Dict[str, Any]:
    """
    Make an HTTP request (GET, POST, etc.) and return the response.
    Parameters:
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
        url (str): The URL to request.
        headers (dict, optional): HTTP headers to include.
        data (str, optional): Raw data to send in the body (for POST/PUT).
        json_data (dict, optional): JSON data to send in the body (for POST/PUT).
        timeout (int, optional): Timeout in seconds (default 10).
    Returns:
        dict: {status_code, headers, text, json (if possible)}
    """
    try:
        resp = requests.request(method, url, headers=headers, data=data, json=json_data, timeout=timeout)
        try:
            resp_json = resp.json()
        except Exception:
            resp_json = None
        return {
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "text": resp.text,
            "json": resp_json
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_and_replace(base_dir: str, path: str, search: str, replace: str, count: int = -1) -> int:
    """
    Search for a string and replace it in a file. Returns the number of replacements made.
    Parameters:
        base_dir (str): The allowed root directory.
        path (str): The relative path to the file.
        search (str): The string to search for.
        replace (str): The string to replace with.
        count (int, optional): Maximum number of replacements (-1 = all).
    Returns:
        int: Number of replacements made.
    """
    abs_path = os.path.join(base_dir, path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content, n = content.replace(search, replace, count), content.count(search) if count == -1 else min(content.count(search), count)
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return n

@mcp.tool()
def file_diff(base_dir: str, path1: str, path2: str, context: int = 3) -> str:
    """
    Show a unified diff between two text files.
    Parameters:
        base_dir (str): The allowed root directory.
        path1 (str): Relative path to the first file.
        path2 (str): Relative path to the second file.
        context (int, optional): Number of context lines (default 3).
    Returns:
        str: Unified diff as a string.
    """
    abs1 = os.path.join(base_dir, path1)
    abs2 = os.path.join(base_dir, path2)
    with open(abs1, 'r', encoding='utf-8') as f1, open(abs2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    diff = difflib.unified_diff(lines1, lines2, fromfile=path1, tofile=path2, n=context)
    return ''.join(diff)

@mcp.tool()
def format_code(base_dir: str, path: str) -> Dict[str, Any]:
    """
    Format a code file using Black (for .py) or Prettier (for .js/.ts). Returns the formatter output.
    Parameters:
        base_dir (str): The allowed root directory.
        path (str): The relative path to the file.
    Returns:
        dict: {"success": bool, "stdout": str, "stderr": str}
    """
    abs_path = os.path.join(base_dir, path)
    ext = os.path.splitext(abs_path)[1].lower()
    if ext == ".py":
        cmd = ["black", abs_path, "--quiet"]
    elif ext in [".js", ".ts"]:
        cmd = ["npx", "prettier", "--write", abs_path]
    else:
        return {"success": False, "stdout": "", "stderr": f"Unsupported file type: {ext}"}
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}

@mcp.tool()
def browser_open_page(url: str) -> str:
    """
    Open a web page and return its HTML content.
    """
    async def _open():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_open())

@mcp.tool()
def browser_screenshot(url: str, path: str = "screenshot.png") -> str:
    """
    Take a screenshot of a web page and save it to a file.
    """
    async def _shot():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        await page.screenshot(path=path)
        await page.close()
        return path
    return asyncio.get_event_loop().run_until_complete(_shot())

@mcp.tool()
def browser_click(url: str, selector: str, wait_for: Optional[str] = None) -> str:
    """
    Open a web page, click an element specified by selector, and return the resulting HTML content.
    Optionally wait for another selector to appear after the click.
    """
    async def _click():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        await page.click(selector)
        if wait_for:
            await page.wait_for_selector(wait_for)
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_click())

@mcp.tool()
def browser_type(url: str, selector: str, text: str, submit_selector: Optional[str] = None, wait_for: Optional[str] = None) -> str:
    """
    Open a web page, type text into an element specified by selector, optionally click a submit button, and return the resulting HTML content.
    Optionally wait for another selector to appear after the action.
    """
    async def _type():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        await page.fill(selector, text)
        if submit_selector:
            await page.click(submit_selector)
        if wait_for:
            await page.wait_for_selector(wait_for)
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_type())

@mcp.tool()
def browser_extract(url: str, selector: str, attr: Optional[str] = None, all_matches: bool = False) -> Any:
    """
    Open a web page and extract data from elements matching the selector.
    If attr is provided, extract that attribute; otherwise, extract inner text.
    If all_matches is True, return a list of all matches; else, return the first match.
    """
    async def _extract():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        if all_matches:
            handles = await page.query_selector_all(selector)
            if attr:
                results = [await h.get_attribute(attr) for h in handles]
            else:
                results = [await h.inner_text() for h in handles]
        else:
            handle = await page.query_selector(selector)
            if handle:
                if attr:
                    results = await handle.get_attribute(attr)
                else:
                    results = await handle.inner_text()
            else:
                results = None
        await page.close()
        return results
    return asyncio.get_event_loop().run_until_complete(_extract())

@mcp.tool()
def browser_wait_for_element(url: str, selector: str, timeout: int = 30000) -> str:
    """
    Open a web page and wait for an element to appear, then return the page content.
    Useful for dynamic content that loads after the initial page load.
    """
    async def _wait():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector(selector, timeout=timeout)
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_wait())

@mcp.tool()
def browser_scroll_and_extract(url: str, selector: str, scroll_selector: Optional[str] = None, max_scrolls: int = 5) -> List[str]:
    """
    Scroll through a page and extract all elements matching the selector.
    Useful for infinite scroll pages or lazy-loaded content.
    """
    async def _scroll_extract():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        
        results = []
        last_height = await page.evaluate("document.body.scrollHeight")
        
        for _ in range(max_scrolls):
            # Extract current elements
            elements = await page.query_selector_all(selector)
            for element in elements:
                text = await element.inner_text()
                if text and text not in results:
                    results.append(text)
            
            # Scroll down
            if scroll_selector:
                await page.click(scroll_selector)
            else:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            await page.wait_for_timeout(2000)  # Wait for content to load
            
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        await page.close()
        return results
    return asyncio.get_event_loop().run_until_complete(_scroll_extract())

@mcp.tool()
def browser_fill_form(url: str, form_data: Dict[str, str], submit_selector: Optional[str] = None, wait_for: Optional[str] = None) -> str:
    """
    Fill out a form with multiple fields and optionally submit it.
    form_data should be a dictionary mapping selectors to values.
    """
    async def _fill_form():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        
        for selector, value in form_data.items():
            await page.fill(selector, value)
        
        if submit_selector:
            await page.click(submit_selector)
        
        if wait_for:
            await page.wait_for_selector(wait_for)
        
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_fill_form())

@mcp.tool()
def browser_handle_dialog(url: str, action: str = "accept", prompt_text: Optional[str] = None) -> str:
    """
    Handle browser dialogs (alerts, confirms, prompts).
    action can be 'accept', 'dismiss', or 'prompt'.
    """
    async def _handle_dialog():
        browser = await get_browser()
        page = await browser.new_page()
        
        if action == "accept":
            page.on("dialog", lambda dialog: dialog.accept())
        elif action == "dismiss":
            page.on("dialog", lambda dialog: dialog.dismiss())
        elif action == "prompt" and prompt_text:
            page.on("dialog", lambda dialog: dialog.accept(prompt_text))
        
        await page.goto(url)
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_handle_dialog())

@mcp.tool()
def browser_upload_file(url: str, file_input_selector: str, file_path: str) -> str:
    """
    Upload a file to a web page using a file input element.
    """
    async def _upload():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        
        with page.expect_file_chooser() as fc_info:
            await page.click(file_input_selector)
        file_chooser = fc_info.value
        await file_chooser.set_files(file_path)
        
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_upload())

@mcp.tool()
def browser_get_network_requests(url: str, request_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Capture network requests made by the page.
    request_type can be 'GET', 'POST', 'XHR', etc.
    """
    async def _capture_requests():
        browser = await get_browser()
        page = await browser.new_page()
        
        requests_data = []
        
        def handle_request(request):
            if not request_type or request.method == request_type:
                requests_data.append({
                    "url": request.url,
                    "method": request.method,
                    "headers": request.headers,
                    "post_data": request.post_data
                })
        
        page.on("request", handle_request)
        await page.goto(url)
        await page.wait_for_timeout(5000)  # Wait for requests to complete
        
        await page.close()
        return requests_data
    return asyncio.get_event_loop().run_until_complete(_capture_requests())

@mcp.tool()
def browser_execute_javascript(url: str, script: str) -> Any:
    """
    Execute custom JavaScript code on the page and return the result.
    """
    async def _execute_js():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        
        result = await page.evaluate(script)
        await page.close()
        return result
    return asyncio.get_event_loop().run_until_complete(_execute_js())

@mcp.tool()
def browser_get_page_info(url: str) -> Dict[str, Any]:
    """
    Get comprehensive information about the page including title, URL, viewport, and more.
    """
    async def _get_info():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        
        info = {
            "title": await page.title(),
            "url": page.url,
            "viewport": await page.viewport_size(),
            "content": await page.content(),
            "text_content": await page.text_content("body"),
            "screenshot": await page.screenshot(type="jpeg", quality=80)
        }
        
        await page.close()
        return info
    return asyncio.get_event_loop().run_until_complete(_get_info())

@mcp.tool()
def browser_navigate_with_cookies(url: str, cookies: List[Dict[str, Any]]) -> str:
    """
    Navigate to a URL with custom cookies set.
    """
    async def _navigate_with_cookies():
        browser = await get_browser()
        page = await browser.new_page()
        
        await page.context.add_cookies(cookies)
        await page.goto(url)
        
        content = await page.content()
        await page.close()
        return content
    return asyncio.get_event_loop().run_until_complete(_navigate_with_cookies())

@mcp.tool()
def browser_compare_pages(url1: str, url2: str, selector: str) -> Dict[str, Any]:
    """
    Compare content between two pages using a specific selector.
    """
    async def _compare():
        browser = await get_browser()
        
        # Get content from first page
        page1 = await browser.new_page()
        await page1.goto(url1)
        content1 = await page1.text_content(selector)
        await page1.close()
        
        # Get content from second page
        page2 = await browser.new_page()
        await page2.goto(url2)
        content2 = await page2.text_content(selector)
        await page2.close()
        
        return {
            "url1": url1,
            "url2": url2,
            "content1": content1,
            "content2": content2,
            "identical": content1 == content2,
            "length_diff": len(content1) - len(content2) if content1 and content2 else None
        }
    return asyncio.get_event_loop().run_until_complete(_compare())

@mcp.tool()
def browser_generate_accessibility_report(url: str) -> Dict[str, Any]:
    """
    Generate an accessibility report for the page using Playwright's built-in accessibility features.
    """
    async def _accessibility_report():
        browser = await get_browser()
        page = await browser.new_page()
        await page.goto(url)
        
        # Get accessibility snapshot
        snapshot = await page.accessibility.snapshot()
        
        # Check for common accessibility issues
        issues = []
        
        # Check for images without alt text
        images = await page.query_selector_all("img")
        for img in images:
            alt = await img.get_attribute("alt")
            if not alt:
                issues.append("Image missing alt text")
        
        # Check for form labels
        inputs = await page.query_selector_all("input")
        for inp in inputs:
            id_attr = await inp.get_attribute("id")
            if id_attr:
                label = await page.query_selector(f"label[for='{id_attr}']")
                if not label:
                    issues.append(f"Input with id '{id_attr}' missing label")
        
        await page.close()
        
        return {
            "url": url,
            "accessibility_snapshot": snapshot,
            "issues_found": issues,
            "total_issues": len(issues)
        }
    return asyncio.get_event_loop().run_until_complete(_accessibility_report())

@mcp.tool()
def math_operation(operation: str, a: float, b: float = None) -> float:
    """
    Perform a math operation. Supported operations: add, subtract, multiply, divide, power, sqrt.
    For 'sqrt', only 'a' is used.
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero.")
        return a / b
    elif operation == "power":
        return a ** b
    elif operation == "sqrt":
        if a < 0:
            raise ValueError("Cannot take sqrt of negative number.")
        return math.sqrt(a)
    else:
        raise ValueError(f"Unsupported operation: {operation}")

@mcp.tool()
def time_operation(operation: str, dt: str = None, fmt: str = None, date_str: str = None) -> Any:
    """
    Perform a time operation. Supported operations:
    - 'now': return current time as ISO string
    - 'today': return current date as YYYY-MM-DD
    - 'timestamp': return current Unix timestamp
    - 'format': format a datetime string (dt) to a custom format (fmt)
    - 'parse': parse a date string (date_str) with a given format (fmt) and return ISO string
    """
    if operation == "now":
        return datetime.datetime.now().isoformat()
    elif operation == "today":
        return datetime.date.today().isoformat()
    elif operation == "timestamp":
        return datetime.datetime.now().timestamp()
    elif operation == "format":
        if not dt or not fmt:
            raise ValueError("'dt' and 'fmt' are required for 'format' operation.")
        d = datetime.datetime.fromisoformat(dt)
        return d.strftime(fmt)
    elif operation == "parse":
        if not date_str or not fmt:
            raise ValueError("'date_str' and 'fmt' are required for 'parse' operation.")
        d = datetime.datetime.strptime(date_str, fmt)
        return d.isoformat()
    else:
        raise ValueError(f"Unsupported operation: {operation}")

@mcp.tool()
def wait_operation(seconds: float, mode: str = "blocking") -> str:
    """
    Wait for a specified number of seconds. Useful for rate limiting, waiting for external events, or simulating delays.
    Parameters:
        seconds (float): Number of seconds to wait (can be fractional).
        mode (str, optional): 'blocking' (default, uses time.sleep) or 'async' (uses asyncio.sleep).
    Returns:
        str: A message indicating the wait is complete.
    """
    if mode == "blocking":
        time.sleep(seconds)
        return f"Waited {seconds} seconds (blocking)."
    elif mode == "async":
        async def _wait():
            await asyncio.sleep(seconds)
            return f"Waited {seconds} seconds (async)."
        return asyncio.get_event_loop().run_until_complete(_wait())
    else:
        raise ValueError("mode must be 'blocking' or 'async'")

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=HOST, port=PORT, path=PATH) 