#! /bin/bash
root=`dirname $0`
cd $root/../..
root=$PWD

docker rm -f airpipeline-dev

docker run -it -d --name airpipeline-dev \
        -p 33134:22 -p 33135:5000 \
        -v /etc/localtime:/etc/localtime \
        -v /var/nfs/general/data:/var/nfs/general/data \
        -v $root:/workspace \
        www.registry.cyber.ai/airenv/python-env:v4.1.1 \
        /usr/sbin/sshd -D
