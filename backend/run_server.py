#!/usr/bin/env python3
"""持久运行后端服务器 - 不会被 shell session 终止"""
import subprocess, sys, os
os.chdir("/home/sandbox/.openclaw/workspace/marketing-leads/backend")
env = os.environ.copy()
env["DEEPSEEK_API_KEY"] = "sk-13b158bfdd454b98855d8d2675683a98"
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8088"],
    env=env, stdout=open("/tmp/backend.log", "a"), stderr=subprocess.STDOUT,
    start_new_session=True
)
print(f"Server PID: {proc.pid}")
