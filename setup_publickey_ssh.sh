#!/bin/bash

# Example Usage: $0 zchen@quake36.suse.de

if [ -z "$1" ]; then
    echo Usage: $0 user@host
    exit -1
fi

pk=`cat ~/.ssh/id_dsa.pub || cat ~/.ssh/id_rsa.pub`

if [ -z "$pk" ]; then
    ssh-keygen -t dsa
fi

ssh $1 "mkdir -p ~/.ssh; echo $pk >> ~/.ssh/authorized_keys"
exit 0
