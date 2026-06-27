#!/usr/bin/env python
"""
将本机摄像头转为 RTSP/HTTP 流
用法: python rtsp_webcam.py [--port 8554] [--camera 0]

使用 MediaMTX 作为 RTSP 服务器（需要先下载）
"""
import argparse
import cv2
import subprocess
import sys
import os
import threading
import time


def find_ffmpeg():
    """自动查找 FFmpeg 路径"""
    candidates = [
        "ffmpeg",
        os.path.expandvars(
            r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
        ),
    ]
    for path in candidates:
        try:
            subprocess.run([path, "-version"], capture_output=True, check=True)
            return path
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            continue
    return None


def download_mediamtx():
    """下载 MediaMTX"""
    import urllib.request
    import zipfile

    url = "https://github.com/bluenviron/mediamtx/releases/download/v1.10.0/mediamtx_v1.10.0_windows_amd64.zip"
    dest = os.path.join(os.path.dirname(__file__), "mediamtx.zip")

    print("正在下载 MediaMTX...")
    try:
        urllib.request.urlretrieve(url, dest)
        with zipfile.ZipFile(dest, 'r') as z:
            z.extractall(os.path.dirname(__file__))
        os.remove(dest)
        print("MediaMTX 下载完成")
        return os.path.join(os.path.dirname(__file__), "mediamtx.exe")
    except Exception as e:
        print(f"下载失败: {e}")
        return None


def find_mediamtx():
    """查找 MediaMTX"""
    candidates = [
        os.path.join(os.path.dirname(__file__), "mediamtx.exe"),
        "mediamtx",
    ]
    for path in candidates:
        try:
            subprocess.run([path, "--version"], capture_output=True, check=True)
            return path
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            continue
    return None


def get_camera_list():
    """列出可用摄像头"""
    cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cameras.append(i)
            cap.release()
    return cameras


def stream_rtsp(camera_id=0, port=8554, ffmpeg_path="ffmpeg"):
    """使用 MediaMTX + FFmpeg 将摄像头转为 RTSP 流"""
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"无法打开摄像头 #{camera_id}")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    fps = int(cap.get(cv2.CAP_PROP_FPS) or 30)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    rtsp_url = f"rtsp://127.0.0.1:{port}/live"
    print(f"\n摄像头 #{camera_id} 已开启 ({width}x{height} @ {fps}fps)")
    print(f"RTSP 地址: {rtsp_url}")
    print(f"按 Ctrl+C 停止\n")

    ff_cmd = [
        ffmpeg_path,
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-b:v", "1M",
        "-f", "rtsp",
        "-rtsp_transport", "tcp",
        rtsp_url,
    ]

    proc = subprocess.Popen(
        ff_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 检查 FFmpeg 是否启动成功
    import time
    time.sleep(1)
    if proc.poll() is not None:
        err = proc.stderr.read().decode('utf-8', errors='ignore')
        print(f"FFmpeg 启动失败: {err}")
        sys.exit(1)
    print("FFmpeg 推流已启动\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            try:
                proc.stdin.write(frame.tobytes())
            except BrokenPipeError:
                print("FFmpeg 连接断开")
                break
    except KeyboardInterrupt:
        print("\n停止推流")
    finally:
        cap.release()
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="本机摄像头 → RTSP 流")
    parser.add_argument("--port", type=int, default=8554, help="RTSP 端口 (默认 8554)")
    parser.add_argument("--camera", type=int, default=0, help="摄像头编号 (默认 0)")
    parser.add_argument("--list", action="store_true", help="列出可用摄像头")
    args = parser.parse_args()

    if args.list:
        cams = get_camera_list()
        if cams:
            print(f"可用摄像头: {cams}")
        else:
            print("未检测到摄像头")
        sys.exit(0)

    # 查找 MediaMTX
    mediamtx_path = find_mediamtx()
    if not mediamtx_path:
        print("未找到 MediaMTX，正在下载...")
        mediamtx_path = download_mediamtx()
        if not mediamtx_path:
            print("请手动下载: https://github.com/bluenviron/mediamtx/releases")
            sys.exit(1)

    # 查找 FFmpeg
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        print("未找到 FFmpeg，请安装:")
        print("  winget install Gyan.FFmpeg")
        sys.exit(1)

    # 启动 MediaMTX（开启 WebRTC）
    print("启动 MediaMTX...")

    # 创建配置文件开启 WebRTC + RTSP + 路径
    config_content = f"""# MediaMTX configuration
rtspAddress: :{args.port}
webrtcAddress: :8889

paths:
  live:
    source: publisher
"""
    config_path = os.path.join(os.path.dirname(__file__), "mediamtx.yml")
    with open(config_path, "w") as f:
        f.write(config_content)

    mt_proc = subprocess.Popen(
        [mediamtx_path, config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)  # 等待 MediaMTX 启动

    # 验证 MediaMTX 是否启动成功
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(("127.0.0.1", args.port))
    sock.close()

    if result != 0:
        print("MediaMTX 启动失败，请检查配置")
        sys.exit(1)

    print("MediaMTX 已启动 (RTSP + WebRTC)")

    stream_rtsp(args.camera, args.port, ffmpeg_path)
