#/!/usr/bin/env python3
#coding=utf-8
import click
import configparser
import jinja2
import json
import yaml
from json import dumps
from yaml import safe_load
from atlassian import Jira

#issue를 delete 할 때 사용할 실패 시 abort fuction
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

#To Do
#.credentials 파일을 --config로 선택할 수 있도록 하고
#default가 아닌 다른 section도 --profile로 선택할 수 있도록 변경 필요
try:
    cred = configparser.RawConfigParser(allow_no_value=True)
    cred.read('.credentials')
    cred.sections()
    url = cred.get('default', 'url')
    username = cred.get('default', 'username')
    password = cred.get('default', 'password')
except Exception as e:
    print(e)

jira = Jira(url, username, password)

@click.group()
def cli(**kwargs):
    pass

@cli.command()
@click.argument('key', type=str, required=True)
def get_issue(key):
    try:
        issue = jira.issue(key)
        click.echo(json.dumps(issue))
    except Exception as e:
        print(e)

@cli.command()
@click.argument('key', type=str, required=True)
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False, prompt='Are you sure delete issue?')
def delete(key):
    try:
        issue = jira.delete_issue(key)
    except Exception as e:
        print(e)

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--project', '-p', 'project', default='default', help='section in project.yaml')
@click.option('--due-date', '-d', 'duedate', help="set due date when project needs ['YYYY-MM-DD']")
@click.option('--yaml', 'yaml', is_flag=True, show_default=True, default=True, help='create issue from yaml')
@click.option('--json', 'json', is_flag=True, show_default=True, default=False, help='create issue from json')
def create_issue(filename, duedate, project, yaml, json):
    try:
        if yaml:
            with open('project.yaml', 'r') as yamlfile:
                data = safe_load(yamlfile)
                config = data[project]
                watchers = list(config['watchers'])
                loader = jinja2.FileSystemLoader(searchpath='./')
                jenv = jinja2.Environment(loader=loader)
                template = jenv.get_template(filename)
                rendered_template = template.render(config)
                fields = safe_load(rendered_template)

                if duedate is not None:
                    fields.update({'duedate': duedate})

                create_issue = jira.create_issue(fields)
                click.echo(dumps(create_issue))
        if json:
            with open(filename, 'r') as fields:
                create_issue(fields)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    cli()