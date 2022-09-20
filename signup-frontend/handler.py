from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("signup-frontend", "templates"),
    autoescape=select_autoescape()
)

dev_url = "https://dev.codex.api.openimagegenius.com/redirect"
prod_url = "https://codex.api.openimagegenius.com/redirect"


def signup(event, context):
    pass


def google_redirect(event, context):
    pass
