#!/usr/bin/env python3
"""FTP upload utility.

Reads secrets from ftp_config.json in project root (NOT committed).

Expected ftp_config.json format:
{
  "host": "ftp.hypechats.com",
  "port": 21,
  "username": "nexuzy@hypechats.com",
  "password": "***",
  "remote_dir": "/home/fenmqwdk/hypechats.com/nexuzy",
  "public_url_base": "https://hypechats.com/nexuzy"
}

Notes:
- Uses plain FTP (port 21). If your server requires explicit FTPS, we can switch to FTP_TLS.
"""

import json
import os
from ftplib import FTP
from pathlib import Path
from typing import Tuple


def load_ftp_config(project_root: Path) -> dict:
    cfg_path = project_root / "ftp_config.json"
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Missing ftp_config.json at {cfg_path}. Create it locally (it is ignored by git)."
        )
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_remote_dir(ftp: FTP, remote_dir: str) -> None:
    # Navigate creating folders if needed
    parts = [p for p in remote_dir.replace('\\', '/').split('/') if p]
    ftp.cwd('/')
    for p in parts:
        try:
            ftp.cwd(p)
        except Exception:
            ftp.mkd(p)
            ftp.cwd(p)


def upload_file(local_path: str, remote_filename: str) -> Tuple[str, str]:
    """Upload a local file to FTP and return (public_url, remote_path)."""
    project_root = Path(__file__).resolve().parent.parent
    cfg = load_ftp_config(project_root)

    host = cfg.get("host")
    port = int(cfg.get("port", 21))
    username = cfg.get("username")
    password = cfg.get("password")
    remote_dir = cfg.get("remote_dir")
    public_url_base = cfg.get("public_url_base")

    if not all([host, username, password, remote_dir, public_url_base]):
        raise ValueError("ftp_config.json missing required fields")

    local_path = str(local_path)
    if not os.path.exists(local_path):
        raise FileNotFoundError(local_path)

    with FTP() as ftp:
        ftp.connect(host=host, port=port, timeout=15)
        ftp.login(user=username, passwd=password)

        ensure_remote_dir(ftp, remote_dir)

        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR {remote_filename}", f)

    remote_path = remote_dir.rstrip('/') + '/' + remote_filename
    public_url = public_url_base.rstrip('/') + '/' + remote_filename
    return public_url, remote_path
