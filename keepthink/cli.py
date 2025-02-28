import click
from keepthink.web.app import app

@click.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=8866, help='Port to listen')
def main(host, port):
    """Start the keepthink web server"""
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()