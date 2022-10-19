#/!/usr/bin/env python3
#coding=utf-8
import click
import configparser
import jinja2
import json
import yaml
from pathlib import Path
from atlassian import Jira

class Creds:
    try:
        cred = configparser.RawConfigParser(allow_no_value=True)
        cred.read('.credentials')
        cred.sections()
        url = cred.get('default', 'url')
        username = cred.get('default', 'username')
        password = cred.get('default', 'password')
    except Exception as e:
        print(e)

jira = Jira(Creds.url, Creds.username, Creds.password)

#issue를 delete 할 때 사용할 실패 시 abort fuction
def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

@click.group()
def cli(**kwargs):
    pass

# # configure
# @cli.command()
# @click.option('--profile', default='default', help='profile name')
# @click.option('--username', prompt=True)
# @click.option('--password', click.prompt=True, hide_input=True, confirmation_prompt=True)
# def configure(profile):
#     """create or modify .credentials for jira cli"""
#     if no

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
            with open('project.yaml', 'r') as yamlfile:
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