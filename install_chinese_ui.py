#!/usr/bin/env python3
"""
一键拉取并安装最新的 FreqUI 中文汉化版到当前 Freqtrade 本地仓库
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def install_chinese_ui():
    repo_root = Path(__file__).parent.resolve()
    dest_folder = repo_root / "freqtrade" / "rpc" / "api_server" / "ui" / "installed"
    dest_folder.mkdir(parents=True, exist_ok=True)
    zip_path = repo_root / "freqUI.zip"

    print("正在拉取最新 FreqUI 中文组件发布包...")
    # 优先使用已登录的 gh CLI 下载，速度最快且自动使用网络代理
    gh_cmd = shutil.which("gh")
    downloaded = False
    if gh_cmd:
        try:
            res = subprocess.run(
                [
                    gh_cmd,
                    "release",
                    "download",
                    "latest",
                    "--repo",
                    "ccxx777/frequi",
                    "-p",
                    "freqUI.zip",
                    "--output",
                    str(zip_path),
                    "--clobber",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            downloaded = True
        except Exception as e:
            print(f"gh cli 下载失败，尝试 requests: {e}")

    if not downloaded:
        import requests

        url = "https://github.com/ccxx777/frequi/releases/latest/download/freqUI.zip"
        print(f"从 {url} 下载...")
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)

    print(f"下载完成，正在解压部署到 {dest_folder}...")
    # 清理旧静态文件（保留 .gitkeep）
    for p in reversed(list(dest_folder.glob("**/*"))):
        if p.name in (".gitkeep", "fallback_file.html"):
            continue
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            p.rmdir()

    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest_folder)

    if zip_path.exists():
        zip_path.unlink()

    with open(dest_folder / ".uiversion", "w", encoding="utf-8") as f:
        f.write("chinese-latest")

    print("FreqUI 中文汉化版安装成功！")


if __name__ == "__main__":
    install_chinese_ui()
