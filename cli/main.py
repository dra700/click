from distutils.command.config import config
import click
import configparser
import json
import yaml
from atlassian import Jira

try:
    cred = configparser.RawConfigParser(allow_no_value=True)
    cred.read('.credentials')
    cred.sections()
    url = cred.get('default', 'url')
    username = cred.get('default', 'username')
    password = cred.get('default', 'password')
except Exception as e:
    print(e)

try:
    with open('project.yaml', 'r') as projct_config:
        data = yaml.safe_load(project_config)
        config = data[project]
        watchers = list(config['watchers'])
except Exception as e:
    print(e)

jira = Jira(url, username, password)

@click.group()
@click.pass_context
def cli(**kwargs):
    pass

@cli.group()
@click.argument('key')
@click.pass_context
def issue(ctx, key):
    ctx.obj = key

@issue.command()
@click.pass_obj
def get(key):
    try:
        issue = jira.issue(key)
        click.echo(json.dumps(issue))
    except Exception as e:
        print(e)

@issue.command()
@click.argument('field', type=str, required=True)
@click.pass_obj
def get_field_value(key, field):
    value = jira.issue_field_value(key, field)
    click.echo(json.dumps(value))

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--project', '-p', 'project', default='default', help='section in project.yaml')
@click.option('--due-date', '-d', 'duedate', help='due date')
@click.option('--yaml', 'yaml', is_flag=True, show_default=True, default=True, help='create issue from yaml')
@click.option('--json', 'json', is_flag=True, show_default=True, default=False, help='create issue from json')
def create_issue(filename, yaml, json):
    click.echo(filename)
    if yaml:
        try:
            with open(filename, 'r') as yamlfile:
                data = yaml.safe_load(yamlfile)
                
        click.echo('yaml!')
    if json:
        click.echo('json!')


if __name__ == '__main__':
    cli()


#to do
#issue에 arg(KEY) 가 없어도 동작할 수 있도록
#TypeError: create() got multiple values for argument 'fields' 문제 해결