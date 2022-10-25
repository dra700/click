#/!/usr/bin/env python3
#coding=utf-8

import os
import click
import configparser
import jinja2
import json
import yaml
from pathlib import Path
from atlassian import Jira

class Config(object):
    def __init__(self, *file_names):
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        found = parser.read(file_names)
        if not found:
            raise ValueError('No config file found!')
        self.__dict__.update(parser.items(profile))
    def update(self, *filenames, profile, url, username, password):
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        if os.path.isfile(filenames):
            parser.read_file(open(filenames))
            parser.read(filenames)
        if not parser.has_section(profile):
            parser.add_section(profile)
        parser.set(profile, 'url', url)
        parser.set(profile, 'username', username)
        parser.set(profile, 'password', password)
#todo url, username, password를 각각 받지 말고 함수 한번에 하나씩 총 3번 호출하는 방식으로 간단하게 변경할 것

profile = 'default'
config_path = Path.home() / '.jira_cli' / 'credentials'
config = Config(config_path)
jira = Jira(config.url, config.username, config.password)

#issue를 delete 할 때 사용할 실패 시 abort fuction
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

# cli
@click.group()
def cli(**kwargs):
    pass

# configure
@cli.command()
@click.option('--profile', default='default', help='profile name')
@click.option('--url', default='https://jira.neowiz.com', prompt=True, help='Set Jira Site URL')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def configure(filenames, profile, url, username, password):
    """create or modify .credentials for jira cli"""
    filenames = config_path
    Config.update(filenames, profile, url)
    Config.update(filenames, profile, username)
    Config.update(filenames, profile, password)

#get issue
@cli.command()
@click.argument('key', type=str, required=True)
def get_issue(key):
    try:
        result = jira.issue(key)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#get issue field value
@cli.command()
@click.argument('key', type=str, required=True)
@click.argument('field', type=str, required=True)
def issue_field_value(key, field):
    try:
        result = jira.issue_field_value(key, field)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#update issue field
@cli.command()
@click.pass_obj
def update_issue_field(key, fields):
    try:
        result = jira.update_issue_field(key, fields)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#delete issue
@cli.command()
@click.argument('key', type=str, required=True)
@click.option('--yes', '-y', is_flag=True, callback=abort_if_false, expose_value=False, prompt='Are you sure delete issue?')
def delete_issue(key):
    try:
        issue = jira.delete_issue(key)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#create issue
@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--project', '-p', 'project', default='default', help='section in project.yaml')
@click.option('--due-date', '-d', 'duedate', help="set due date when project needs ['YYYY-MM-DD']")
@click.option('--yaml', 'input_yaml', is_flag=True, show_default=True, default=True, help='create issue from yaml')
@click.option('--json', 'input_json', is_flag=True, show_default=True, default=False, help='create issue from json')
def create_issue(filename, duedate, project, input_yaml, input_json):
    try:
        if input_yaml:
            with open('../../project.yaml', 'r') as yamlfile:
                data = yaml.safe_load(yamlfile)
                config = data[project]
                watchers = list(config['watchers'])
                loader = jinja2.FileSystemLoader(searchpath='./')
                jenv = jinja2.Environment(loader=loader)
                template = jenv.get_template(filename)
                rendered_template = template.render(config)
                fields = yaml.safe_load(rendered_template)

                if duedate is not None:
                    fields.update({'duedate': duedate})

                create_issue = jira.create_issue(fields)
                click.echo(json.dumps(create_issue))
        if input_json:
            with open(filename, 'r') as fields:
                create_issue(fields)
    except Exception as e:
        print(e)



if __name__ == '__main__':
    cli()