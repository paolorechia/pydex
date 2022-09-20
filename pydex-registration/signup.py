import os

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("template_app", "templates"), autoescape=select_autoescape()
)

urls = {
    "dev": "https://dev.codex.api.openimagegenius.com/redirect",
    "prod": "https://codex.api.openimagegenius.com/redirect",
}

signup_template = env.get_template("signup.html")
stage = os.environ["STAGE"]


def signup(event, context):
    html = signup_template.render(url=urls[stage])
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
