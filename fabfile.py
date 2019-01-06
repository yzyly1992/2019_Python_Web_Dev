#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'David Yang'

import os, re
from datetime import datetime

# 导入Fabric API:
from fabric.api import *

# 服务器登录用户名和秘钥:
env.hosts = ['ubuntu@xxxx.xxxx.compute.amazonaws.com']
env.key_filename = '/xxx/xxx/awsKeyPair.pem'

# 服务器MySQL用户名和口令:
db_user = 'root'
db_password = 'MySQL的root用户密码'

_TAR_FILE = 'dist-awesome.tar.gz'
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/awesome'

def deploy():
    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    # 删除已有的tar文件:
    run('rm -f %s' % _REMOTE_TMP_TAR)
    # 上传新的tar文件:
    put('dist/%s' % _TAR_FILE, _REMOTE_TMP_TAR)
    # 创建新目录:
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    # 解压到新目录:
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
        # 需要添加权限浏览器才能访问
        sudo('chmod -R 775 static/')
        sudo('chmod 775 favicon.ico')
        # # 由于app.py的文件格式有问题，转换一下
        # run('app.py')
    # 重置软链接:
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -rf www')
        sudo('ln -s %s www' % newdir)
        sudo('chown ubuntu:ubuntu www')
        sudo('chown -R ubuntu:ubuntu %s' % newdir)
    # 重启Python服务和nginx服务器:
    with settings(warn_only=True):
        sudo('supervisorctl stop awesome')
        sudo('supervisorctl start awesome')
        sudo('/etc/init.d/nginx reload')


def build():
    includes = ['static', 'templates', 'transwarp', 'favicon.ico', '*.py', '*.txt']
    excludes = ['test', '.*', '*.pyc', '*.pyo']
    local('rm -f dist/%s' % _TAR_FILE)
    with lcd(os.path.join(os.path.abspath('.'), 'www')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s' % _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))