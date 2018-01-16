#!/bin/bash
export S3_BUCKET=kiwi-k8s-state-store
export KOPS_STATE_STORE=s3://${S3_BUCKET}
export AWS_AVAILABILITY_ZONES=us-east-1a,us-east-1b
export NAME=kiwi.k8s.local

echo "create S3 bucket $S3_BUCKET"
aws s3api create-bucket \
--bucket $S3_BUCKET \
--region us-east-1