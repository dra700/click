import string
import click
import configparser
import json
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

jira = Jira(url, username, password)

@click.group()
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
    issue = jira.issue(key)
    click.echo(json.dumps(issue))

@issue.command()
@click.argument('field', type=str, required=True)
@click.pass_obj
def get_field_value(key, field):
    value = jira.issue_field_value(key, field)
    click.echo(json.dumps(value))

@issue.command()
@click.argument('fields', type=dict, required=True)
def create(fields):
    result = jira.issue_create(fields)
    click.echo(json.dumps(result))

if __name__ == '__main__':
    cli()