#/!/usr/bin/env python3
#coding=utf-8

import os
import click
import configparser
import jinja2
import json
import yaml
#from pathlib import Path
from atlassian import Jira

class Config(object):
    def __init__(self, filename):
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        found = parser.read(filename)
        try:
            if not found:
                raise ValueError("No config found. run 'jira-cli configure' first")
            self.__dict__.update(parser.items(profile))
        except ValueError or configparser.NoOptionError or configparser.NoOptionError as e:
            print(e)
    def update(self, filename, profile, key, value):
        parser = configparser.RawConfigParser()
        parser.optionxform = str
        if os.path.isfile(filename):
            parser.read_file(open(filename))
            parser.read(filename)
        if not parser.has_section(profile):
            parser.add_section(profile)
        parser.set(profile, key, value)
        with open(filename, 'w') as f:
            parser.write(f)

profile = 'default'
config_path = os.path.join(os.path.expanduser('~'), '.jira_cli', 'credentials') # config path = ~/.jira_cli/credentials
try:
    config = Config(config_path)
    jira = Jira(config.url, config.username, config.password)
except AttributeError as e:
    print(e)

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
def configure(profile, url, username, password):
    '''create or modify ~/.jira_cli/credentials for jira cli'''
    config = Config(config_path)
    d = {'url': url, 'username': username, 'password': password}
    try:
        for key, value in d.items():
            config.update(config_path, profile, key, value)
    except Exception as e:
        print(e)

#get issue
@cli.command()
@click.argument('key', type=str, required=True)
def get_issue(key):
    '''get issue from issue key'''
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
    '''get issue field from issue key'''
    try:
        result = jira.issue_field_value(key, field)
        click.echo(json.dumps(result))
    except Exception as e:
        print(e)

#update issue field
@cli.command()
@click.pass_obj
def update_issue_field(key, fields):
    '''update issue field'''
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
    '''delete issue from issue key'''
    try:
        issue = jira.delete_issue(key)
        click.echo(json.dumps(issue))
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
    '''create issue from yaml template'''
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