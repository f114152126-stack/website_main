# Sets up the routes for all the pages

from flask import Flask, render_template, request, make_response, session
from flask_caching import Cache
from config import TEMPLATES_PATH, TEXT_PATH
from application.helpers import *
from openai import OpenAI
import os


app = Flask(__name__, template_folder=TEMPLATES_PATH)
app.jinja_env.filters["is_active"] = is_active
app.jinja_env.filters["get_language_image"] = get_language_image
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
app.secret_key = os.getenv("SECRET_KEY")
app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600
cache = Cache(app)


@app.route("/")
def loading():
    """Renders the 'Loading' page of the website."""

    #response = make_response(render_template("loading.html"))
    #response.headers["Cache-Control"] = "public, max-age=3"

    #return response
    return render_template("home.html")


@app.route("/home")
@cache.cached()
def home():
    """Renders the 'Home' page of the website."""

    return render_template("home.html")


@app.route("/about")
@cache.cached()
def about():
    """Renders the 'About Me' page of the website."""

    content = read_description(f"{TEXT_PATH}/about.txt")

    return render_template("about.html", content=content)


@app.route("/skills", methods=["GET", "POST"])
def skills():

    if "messages" not in session:
        session["messages"] = []

    if request.method == "POST":

        prompt = request.form.get("prompt")

        session["messages"].append({
            "role": "user",
            "content": prompt
        })

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        answer = response.output_text

        session["messages"].append({
            "role": "assistant",
            "content": answer
        })

        session.modified = True

    return render_template(
        "skills.html",
        messages=session["messages"]
    )

# @app.route("/portfolio")
# @cache.cached()
# def portfolio():
#     """Renders the 'Portfolio' page of the website."""

#     repos = get_repositories()

#     return render_template("portfolio.html", repos=repos)

@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():

    image_url = None

    if request.method == "POST":

        prompt = request.form.get("prompt")

        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        image_url = result.data[0].url

    return render_template(
        "portfolio.html",
        image_url=image_url
    )


@app.route("/contact", methods=["GET", "POST"])
@cache.cached()
def contact():
    """Renders the 'Contact' page of the website."""

    # User reached route via POST
    if request.method == "POST":
        return render_template("result.html")

    # User reached route via GET
    return render_template("contact.html")


@app.route("/result")
@cache.cached()
def result():
    """Renders the 'Result' page of the website."""

    return render_template("result.html")
