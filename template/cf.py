#!/usr/bin/env python
import argparse
import boto3
import yaml

__Author__ = 'Yufei Ren'
__Date__ = '2017.11.26'
USAGE = '''
Usage:
    python {script_name} {env} {stack}
Example:
    cd kiwi-cloudformation
    python ./template/cf.py build dev stackname
'''

class CfScript:
    def __init__(self, env, stack):
        """
        init function
        :param env:
        :param stack:
        """
        self.stack_cf = ''
        self.env = env
        self.stack = stack
        self.bucket_name = '{}-cloudformation-scripts'.format(env)
        self.output_folder = './output/' # local output folder
        self.common_files_folder = './common_cloudformation/' 