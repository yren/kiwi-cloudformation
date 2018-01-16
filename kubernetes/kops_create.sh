#!/bin/bash
kops create cluster $NAME \
--cloud aws \
--state $KOPS_STATE_STORE \
--zones=$AWS_AVAILABILITY_ZONES \
--vpc=vpc-20747358 \
--topology=private \
--networking=flannel-vxlan \
--node-security-groups sg-743e7300 \
--master-security-groups sg-743e7300