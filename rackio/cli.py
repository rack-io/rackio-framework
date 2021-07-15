import os
import click
import sys
from dotenv import load_dotenv

_cwd = os.getcwd()
sys.path.append(_cwd)

# System

@click.command()
@click.argument('keywords')
@click.option('--port', '-p', default='8000', help='Application port')
@click.option('--name', '-n', default='', help='Application name')
def rackio_cli(keywords, port, name):

    if keywords == "serve":

        dotenv_path = os.path.join(_cwd, '.env')
        load_dotenv(dotenv_path)

        rackio_app = os.environ.get("RACKIO_APP").replace('.py', '')

        if not rackio_app:

            try:
                module = __import__("app")
            except Exception as e:
                print(e)

            try:
                module = __import__("wsgi")
            except:
                pass
        else:

            try:
                module = __import__(rackio_app)
            except Exception as e:
                print(e)
                return
        
        attrs = dir(module)

        if "app" in attrs:
            app = module.app
        elif "application" in attrs:
            app = module.application
        elif "create_app" in attrs:
            app = module.create_app()
        elif "make_app" in attrs:
            app = module.make_app()
        
        app.run(port=port, app_name=name)
