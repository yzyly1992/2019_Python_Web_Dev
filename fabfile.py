#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'David Yang'

import os, re
from datetime import datetime

# 导入Fabric2:
from fabric import Connection
from fabric import task

# 建立Connection到server:
c = Connection(
    host="your_host_address",
    ## 记得在下面在重置软链那里更改4次your_user_name
    user="your_user_name",
    connect_kwargs={
        "key_filename": "/your/key/location/xxx.pem",
    },
)

_TAR_FILE = 'dist-awesome.tar.gz'
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/awesome'

# 远程部署任务
@task
def deploy(conn):
    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    # 删除已有的tar文件:
    c.run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件:
    c.put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 创建新目录:
    c.sudo('bash -c "cd %s && mkdir %s"' % (_REMOTE_BASE_DIR, newdir))
    # 解压到新目录, 添加浏览权限:
    c.sudo('bash -c "cd %s/%s && tar -xzvf %s && chmod -R 775 static/ && chmod 775 favicon.ico"' % (_REMOTE_BASE_DIR, newdir, _REMOTE_TMP_TAR))
    # 重置软链接,记得下面更改4次your_user_name:
    c.sudo('bash -c "cd %s && rm -rf www && ln -s %s www && chown your_user_name:your_user_name www && chown -R your_user_name:your_user_name %s"' % (_REMOTE_BASE_DIR, newdir, newdir))
    # 重启Python服务和nginx服务器:
    c.sudo('supervisorctl restart awesome', warn=True)
    c.sudo('nginx -s reload', warn=True)

# 打包本地文件
@task
def build(conn):
    includes = ['static', 'templates', 'favicon.ico', '*.py', 'manifest.json', 'sw.js']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    conn.run('rm -f dist/%s' % _TAR_FILE)
    run_path = os.path.join(os.path.abspath('.'), 'www')
    with conn.cd(run_path):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        conn.run(' '.join(cmd))