import click

from dotenv import load_dotenv

# System

@click.command()
@click.argument('keywords')
def rackio_cli(keywords):

    if keywords == "serve":

        load_dotenv()