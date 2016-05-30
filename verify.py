#!/usr/bin/env python
from __future__ import print_function
import rdoinfo
import yaml


def verify(fn):
    info = rdoinfo.parse_info_file(fn)
    print(yaml.dump(info))
    print("\n%s looks OK" % fn)


if __name__ == '__main__':
    verify('rdo.yml')
