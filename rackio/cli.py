import os
import click

from dotenv import load_dotenv

# System

@click.command()
@click.argument('keywords')
def rackio_cli(keywords):

    if keywords == "serve":

        load_dotenv()

        rackio_app = os.getenv("RACKIO_APP")

        if not rackio_app:

            try:
                module = __import__("app")
            except:
                pass

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
        
        app.run()
