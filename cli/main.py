import click

@click.group()
def cli(**kwargs):
    print(1)

@cli.group()
@click.option("--something")
@click.option("--else")
def what(**kwargs):
    print(2)

@what.command()
@click.option("--chaa")
def ever(**kwargs):
    print(3)

if __name__ == '__main__':
    cli()
