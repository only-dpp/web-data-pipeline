from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_digest_html(digest_data: dict) -> str:
    template = env.get_template("digest_email.html")
    

    return template.render(
    digest=digest_data,
    now=datetime.now().strftime("%d %B %Y")
)


def render_welcome_email_html(subscriber_email: str) -> str:
    template = env.get_template("welcome_email.html")

    return template.render(
        subscriber_email=subscriber_email,
        now=datetime.now().strftime("%d %B %Y"),
    )
