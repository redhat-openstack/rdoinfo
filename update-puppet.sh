#!/bin/bash -xe

rm -rf modules
mkdir -p modules

for url in $(cat rdo.yml | grep 'puppet' | grep 'git://github' | awk '{print $2}'); do
    module=$(basename $url)
    git clone $url modules/$module
    set +e
    tag=$(cd modules/$module; git describe --tags $(git rev-list --tags --max-count=1))
    # some modules don't have tag
    if [ "$?" -eq "0" ] ; then
        echo "$module===$tag">>upper-constraints.txt
    fi
    set -e
    rm -rf modules/$module
done

python update-uc.py
