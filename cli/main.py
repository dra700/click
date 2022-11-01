#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# from __future__ import print_function, absolute_import

# import click_completion
# import click_completion.core

import os
import sys
import click
import configparser
import git
import jinja2
import json
import yaml
import git
from atlassian import Jira

# click_completion.init()

# def install_callback(ctx, attr, value):
#     if not value or ctx.resilient_parsing:
#         return value
#     shell, path = click_completion.core.install()
#     click.echo('%s completion installed in %s' % (shell, path))
#     exit(0)

class Config(object):
    def __init__(self, profile, filename):
        if not os.path.isfile(filename):
            sys.exit("Config file not found. run 'jira-cli configure' first")
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        parser.read(filename)
        self.__dict__.update(parser.items(profile))

#config 파일을 만들 때 사용하는 함수. Config class에 구현하려 했으나 __init__에서 config file이 없을 경우 더 이상 실행되지 않도록 처리해야 하기 때문에 configure를 실행할 수 없어 함수 분리함 
def write_config(config_path, profile, k, v):
    try:
        parser = configparser.ConfigParser(interpolation=None)
        splitted_path = os.path.split(config_path)
        config_home = splitted_path[0]
        if not os.path.exists(config_home):
            os.makedirs(config_home)
        if os.path.isfile(config_path):
            parser.read_file(open(config_path))
            parser.read(config_path)
        if not parser.has_section(profile):
            parser.add_section(profile)
        parser.set(profile, k, v)
        with open(config_path, 'w') as f:
            parser.write(f)
    except Exception as e:
        print(e)
        sys.exit(1)

#issue를 delete 할 때 사용할 실패 시 abort 함수
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

#project.yaml 파일을 찾기 위해 git repo 최상위 디렉토리를 알아내는 함수
def get_git_root(path):
    repo = git.Repo(path, search_parent_directories=True)
    result = repo.working_dir
    return result

#yaml 파일을 jinja templating
def create_fields_from_yaml(project, envfile, template_file):
    with open(envfile, 'r') as env_file:
        env = yaml.safe_load(env_file)
        config = env[project]
        watchers = list(config['watchers'])
        loader = jinja2.FileSystemLoader(searchpath='./')
        jenv = jinja2.Environment(loader=loader)
        template = jenv.get_template(template_file)
        rendered_template = template.render(config)
        fields = yaml.safe_load(rendered_template)
        return fields

#json 파일을 fields 로 return
def create_fields_from_json(filename):
    with open(filename, 'r') as json_file:
        fields = json.load(json_file)
        return fields

config_path = os.path.join(os.path.expanduser('~'), '.jira_cli/', 'credentials') # config path = ~/.jira_cli/credentials

# cli
@click.group()
def cli(**kwargs):
    '''jira command line interface (cli)'''
    pass

# # completion
# @cli.command()
# @click.option('--install', is_flag=True, callback=install_callback, expose_value=False, help='Install completion for thr current shell.')
# @click.option('--upper/--lower', default=None, help='Change text to upper or lower case')
# @click.argument('args', nargs=-1)
# def completion(upper, args):
#     '''just print the command line arguments'''
#     if upper:
#         args = [arg.upper() for arg in args]
#     elif upper is not None:
#         args = [arg.lower() for arg in args]
#     click.echo(' '.join(args))

# configure
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.option('--url', default='https://jira.neowiz.com', prompt=True, help='Set Jira Site URL')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def configure(profile, url, username, password):
    '''create or modify config in ~/.jira_cli/credentials'''
    d = {'url': url, 'username': username, 'password': password}
    try:
        for k, v in d.items():
            write_config(config_path, profile, k, v)
    except Exception as e:
        print(e)
    print("Config stored in {}\nSet profile[{}] complete!".format(config_path, profile))

#get issue
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.argument('key', type=str, required=True)
def get_issue(profile, key):
    '''get issue via issue key'''
    config = Config(profile, config_path)
    jira = Jira(config.url, config.username, config.password)
    try:
        result = jira.issue(key)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#get issue field value
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.argument('key', type=str, required=True)
@click.argument('field', type=str, required=True)
def issue_field_value(profile, key, field):
    '''get issue field via issue key'''
    config = Config(profile, config_path)
    jira = Jira(config.url, config.username, config.password)
    try:
        result = jira.issue_field_value(key, field)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#update issue field
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.option('--add-field', 'add_field', type=(str, str), default=None, multiple=True, required=True, help="add field like --add-field customfield_10002 EXAMPLE-735")
@click.argument('key', type=str, required=True)
def update_issue_field(profile, key, add_field):
    '''update issue field'''
    config = Config(profile, config_path)
    jira = Jira(config.url, config.username, config.password)
    d = dict(add_field)
    try:
        result = jira.update_issue_field(key, d)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#delete issue
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.option('--yes', '-y', is_flag=True, callback=abort_if_false, expose_value=False, prompt='Are you sure delete issue?')
@click.argument('key', type=str, required=True)
def delete_issue(profile, key):
    '''delete issue via issue key'''
    config = Config(profile, config_path)
    jira = Jira(config.url, config.username, config.password)
    try:
        issue = jira.delete_issue(key)
        click.echo(json.dumps(issue))
    except Exception as e:
        print(e)

#create issue via template
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.option('--project', '-p', 'project', default='default', help='section in project.yaml')
@click.option('--add-field', 'add_field', type=(str, str), default=None, multiple=True, help="add field like --add-field duedate 2022-10-31")
@click.option('--output-json', 'output_json', is_flag=True, show_default=True, default=False, help='when create issue from yaml, print json input to jira rest api')
@click.argument('filenames', nargs=-1, type=click.Path(exists=True))
def create_issue(profile, filenames, add_field, project, output_json):
    '''create issue via yaml template files'''
    config = Config(profile, config_path)
    jira = Jira(config.url, config.username, config.password)
    git_root = get_git_root('.')
    envfile = os.path.join(git_root, 'project.yaml')
    for filename in filenames:
        fields = create_fields_from_yaml(project, envfile, filename)
        if add_field is not None:
            d = dict(add_field)
            fields.update(d)
        create_issue = jira.create_issue(fields)
        click.echo(create_issue['key'])

#create issue via json
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.argument('filenames', nargs=-1, type=click.Path(exists=True))
def create_issue_from_json(profile, filenames):
    '''create issue via json files'''
    config = Config(profile, config_path)
    jira = Jira(config.url, config.username, config.password)
    for filename in filenames:
        fields = create_fields_from_json(filename)
        create_issue = jira.create_issue(fields)
        click.echo(json.dumps(create_issue))


if __name__ == '__main__':
    cli()