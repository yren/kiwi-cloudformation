#!/usr/bin/env python
import argparse
import yaml
from jinja2 import Environment

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
            if self.config['template'].endwith('yaml.j2'):
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'The command build aws resources via CloudFormation')
    subparsers = parser.add_subparsers(dest = 'sub_command')

    # build
    parser_build = subparsers.add_parser('build', help = 'generate stack cf file')
    parser_build.add_argument('env', help = 'environment')
    parser_build.add_argument('stack', help = 'cloudformation stack name')

    args = parser.parse_args()

    if args.sub_command == 'build':
        cf_script = CfScript(args.env, args.stack)
        cf_script.generate()