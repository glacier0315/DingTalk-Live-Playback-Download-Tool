#!/usr/bin/env python3
"""钉钉直播回放下载工具 CLI入口"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.main import main


def entry_point():
    """CLI入口函数"""
    main()


if __name__ == '__main__':
    entry_point()
