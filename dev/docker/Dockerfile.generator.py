#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2
import os
import requests
import json
from distutils.version import LooseVersion #, StrictVersion
import codecs
import datetime
from jinja2.environment import Environment
import subprocess
import sys

# 0) The basic settings
tpl_dir = os.path.dirname(os.path.abspath(__file__))
tar_dir = tpl_dir

author = 'Jorrit Wronski'
email = 'jowr@ipu.dk'

tpl_first_line = "{0} CAUTION: This file is automatically generated from {1}, do not edit it manually.\n"
tpl_mtime_line = datetime.datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%Y-%m-%d %H:%M')

os.chdir(tpl_dir)
loader = jinja2.FileSystemLoader(['.'])
environment = jinja2.Environment(loader=loader)

# 1) System packages
lin_dev_pkgs =  ["python-dev", "python-pip", "build-essential" ]
lin_dev_pkgs += ["libhdf5-serial-dev", "libnetcdf-dev", "liblapack-dev", "libatlas-dev"]
lin_dev_pkgs += ["gfortran", "gcc", "cmake", "bash", "rsync", "git"]
lin_dev_pkgs += ["curl", "wget"]

# 2) pip packages 
pip_dev_pkgs = ["buildbot-slave"]
pip_pkgs = ["numpy", "scipy", "matplotlib", "pandas"]
pip_add_pkgs = ["wheel"]

# 3) conda packages
cnd_env = ["CoolProp27", "CoolProp33", "CoolProp34"]
cnd_pyt = ["python=2.7", "python=3.3", "python=3.4"]


cnd_dev_pkgs =  ["cython", "pip", "jinja2", "pyyaml", "pycrypto"]
cnd_run_pkgs =  ["numpy", "scipy", "matplotlib", "pandas"]
#cnd_dev_pkgs += ["pywin32", "unxutils", "ndg-httpsclient"]
#cnd_dev_pkgs += ["ndg-httpsclient"]

# 4) Known hosts
#ssh_hosts = ["bitbucket.org", "github.com", "coolprop.dreamhosters.com", "coolprop.org"]

#
local_dict = dict(
  author = author,
  email  = email,
  lin_dev_pkgs = lin_dev_pkgs,
  pip_dev_pkgs = pip_dev_pkgs,
  pip_add_pkgs = pip_add_pkgs,
  cnd_env_pyt = [str(x[0])+" "+str(x[1]) for x in zip(cnd_env,cnd_pyt)],
  cnd_env = cnd_env,
  cnd_dev_pkgs = cnd_dev_pkgs+cnd_run_pkgs,
)
#
template_path = 'Dockerfile.slave.base.tpl'
template = environment.get_template(template_path)
f = codecs.open(os.path.join(tar_dir,'slavebase','Dockerfile'),mode='wb',encoding='utf-8')
f.write(tpl_first_line.format("# "+tpl_mtime_line,template_path))
f.write(template.render(**local_dict))
f.close()
#
template_path = 'Dockerfile.slave.python.tpl'
template = environment.get_template(template_path)
f = codecs.open(os.path.join(tar_dir,'slavepython','Dockerfile'),mode='wb',encoding='utf-8')
f.write(tpl_first_line.format("# "+tpl_mtime_line,template_path))
f.write(template.render(**local_dict))
f.close()


print(r"""
Delete all docker containers: docker stop `docker ps -aq`; docker rm `docker ps -aq`;
Delete all dangling docker images: docker rmi `docker images -f "dangling=true" -q`;

Generate Dockerfiles: python Dockerfile.generator.py
Build images:
docker build -t coolprop/slavebase -f Dockerfile.slave.base . && \
docker build -t coolprop/slavepython -f Dockerfile.slave.python . 

Start the images with:
docker run --env-file ./Dockerfile.slave.env.list --name="slavename" coolprop/slavepython

and the remember to copy your SSH keys to the image:
docker cp ${HOME}/.ssh slavename:/home/buildbot/
docker exec slavename chown -R buildbot /home/buildbot/.ssh


""")


