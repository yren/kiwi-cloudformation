#!/usr/bin/env python
import argparse
import yaml
import boto3
import os
from jinja2 import Environment
from subprocess import call

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

        with open('properties/env.yml', 'r') as stream:
            env_config = yaml.load(stream)
            if self.env in env_config:
                self.config_file = env_config[self.env]
            else:
                raise Exception('Invalid env: [' + self.env + ']')

        with open("properties/{}".format(self.config_file), 'r') as stream:
            all_config = yaml.load(stream)
            if self.stack in all_config:
                self.config = all_config[self.stack]
            else:
                raise Exception('Invalid stack: [' + self.stack + ']')

            self.template_file = 'template/{}'.format(self.config['template'])
            if self.config['template'].endswith('yaml.j2'):
                self.stack_cf_file = '{}.yaml'.format(stack)
            else:
                self.stack_cf_file = '{}.json'.format(stack)

            with open(self.template_file) as tf:
                self.template = Environment().from_string(tf.read())

    def generate(self):
        """
        generate stack cloudformation file
        """
        try:
            self.stack_cf = self.template.render(stack=self.stack, env=self.env, config=self.config)
            with open(self.output_folder + self.stack_cf_file, 'w') as cffile:
                cffile.write(self.stack_cf)
            print('[' + self.stack + '] generate in ' + self.output_folder + self.stack_cf_file)
        except:
            print('[' + self.stack + '] generate cloudformation file failed.')
            raise Exception('Stack ' + self.stack + ' generate cloudformation file failed.')

    def upload(self):
        '''
        upload local cloudformation file to s3
        '''
        boto3.resource('s3').Object(self.bucket_name, self.stack_cf_file).upload_file(self.output_folder + self.stack_cf_file)
        print('[' + self.stack + '] upload to \nhttps://s3.amazonaws.com/' + self.bucket_name + '/' + self.stack_cf_file)

        for file in os.listdir(self.common_files_folder):
            if file.startswith('common_'):
                boto3.resource('s3').Object(self.bucket_name, file).upload_file(self.common_files_folder + file)
                print('https://s3.amazonaws.com/' + self.bucket_name + '/' + file)

    def deploy(self):
        '''
        deploy cloudformation script
        eg: aws cloudformation deploy --stack-name devkiwi --template-file output/kiwi.yaml --parameters-overrides RootVolSize=17
        '''
        command = ['aws', 'cloudformation', 'deploy',
                    '--stack-name', self.env + self.stack,
                    '--capabilities', 'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM',
                    '--template-file', self.output_folder + self.stack_cf_file,
                    '--parameter-overrides',
                    'Env=' + self.env]

        print('[' + self.stack + '] parameters: ')
        print('[' + self.stack + '] Env -> ' + self.env)

        if 'Parameters' in self.config:
            for key, value in self.config['Parameters'].items():
                command.append(key + '=' + str(value))
                print('[' + self.stack + '] key -> ' + str(value))

        print('[' + self.stack + '] ' + ' '.join(map(str, command))
        call(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'The command build aws resources via CloudFormation')
    subparsers = parser.add_subparsers(dest = 'sub_command')

    # build
    parser_build = subparsers.add_parser('build', help = 'generate stack cf file')
    parser_build.add_argument('env', help = 'environment')
    parser_build.add_argument('stack', help = 'cloudformation stack name')

    # stage
    parser_stage = subparsers.add_parser('stage', help = 'generat stack cf file and upload to s3')
    parser_stage.add_argument('env', help = 'environment')
    parser_stage.add_argument('stack', help = 'cloudformation stack name')

    # deploy
    parser_deploy = subparsers.add_parser('deploy', help = 'generat stack cf file and upload to s3, deploy cf stack')
    parser_deploy.add_argument('env', help = 'environment')
    parser_deploy.add_argument('stack', help = 'cloudformation stack name')

    args = parser.parse_args()

    if args.sub_command == 'build':
        cf_script = CfScript(args.env, args.stack)
        cf_script.generate()
    if args.sub_command == 'stage':
        cf_script = CfScript(args.env, args.stack)
        cf_script.generate()
        cf_script.upload()
    if args.sub_command == 'deploy'
        cf_script = CfScript(args.env, args.stack)
        cf_script.generate()
        cf_script.upload()
        cf_script.deploy()