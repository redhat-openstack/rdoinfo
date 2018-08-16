#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import rdoinfo
import sh
import shutil
import sys

if len(sys.argv) > 1:
    UC_RELEASE = sys.argv[1]
else:
    UC_RELEASE = 'stein-uc'


def update_puppet_uc():
    if os.path.exists(os.path.join(".", "modules")):
        shutil.rmtree("./modules")

    info = rdoinfo.parse_info_file('rdo.yml')

    puppet_info = []
    for package in info['packages']:
        if package['name'].startswith('puppet'):
            puppet_info.append([package['name'], package['upstream']])

    for package in puppet_info:
        url = package[1]
        if 'openstack' in url:  # Do not bump OpenStack modules
            continue
        module = package[0]
        gitpath = os.path.join("modules", module)
        sh.git.clone(url, gitpath)
        git = sh.git.bake(_cwd=gitpath, _tty_out=False)
        try:
            rev_list = str(git('rev-list', '--tags', '--max-count=1')).strip()
            tag = str(git.describe('--tags', rev_list)).strip()
            with open('upper-constraints.txt', 'a') as fp:
                fp.write("%s===%s\n" % (module, tag))
        except Exception:
            continue
        shutil.rmtree(gitpath)

    update_uc = sh.Command('./update-uc.py')
    update_uc(UC_RELEASE)

if __name__ == '__main__':
    update_puppet_uc()
