# Sets up the routes for all the pages

import random
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

# -------------------------
# 隨機素材（作為 prompt seed）
# -------------------------

worlds = [
    "科技與魔法並存的世界",
    "AI統治的未來都市",
    "廢土後文明重建世界",
    "太空殖民地",
    "隱藏在人類社會的地下世界"
]

conflicts = [
    "資源爭奪戰",
    "AI與人類衝突",
    "秘密組織操控世界",
    "古代力量復甦",
    "政府實驗失控"
]

arcs = [
    "逐漸發現自己被改造過",
    "追尋失去的記憶",
    "被迫成為關鍵人物",
    "在命運中掙扎",
    "成為改變世界的核心"
]

plots = [
    "阻止世界崩壞",
    "揭開真相",
    "對抗強大勢力",
    "拯救重要的人",
    "改寫世界秩序"
]


# -------------------------
# Step 1: 生成 prompt seed
# -------------------------

def build_seed(job, gender, height):
    return {
        "world": random.choice(worlds),
        "conflict": random.choice(conflicts),
        "arc": random.choice(arcs),
        "plot": random.choice(plots),
        "job": job,
        "gender": gender,
        "height": height
    }


# -------------------------
# Step 2: 轉成 AI Prompt（關鍵）
# -------------------------

def build_prompt(seed):
    return f"""
You are a professional story writer.

Create a cinematic character story package.

Requirements:
- Output in Traditional Chinese
- Make it vivid and narrative-driven

Character Information:
- Job: {seed['job']}
- Gender: {seed['gender']}
- Height: {seed['height']} cm

World Setting:
{seed['world']}

Conflict:
{seed['conflict']}

Character Arc Hint:
{seed['arc']}

Main Plot Hint:
{seed['plot']}

Please output in the following structure:

1. World Background (世界觀)
2. Character Story (人物故事)
3. Main Story (主要故事)

Make it immersive and coherent.
"""

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

    world = None
    character = None
    story = None

    if request.method == "POST":

        job = request.form.get("job")
        gender = request.form.get("gender")
        height = request.form.get("height")

        seed = build_seed(job, gender, height)
        prompt = build_prompt(seed)

        # 🔥 OpenAI call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional narrative designer."},
                {"role": "user", "content": prompt}
            ]
        )

        output = response.choices[0].message.content

        # 👉 簡單切割（如果模型照格式輸出）
        try:
            parts = output.split("\n\n")
            world = parts[0]
            character = parts[1]
            story = parts[2]
        except:
            world = output
            character = ""
            story = ""

    return render_template(
        "portfolio.html",
        world=world,
        character=character,
        story=story
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
