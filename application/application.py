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
# 隨機素材庫（核心）
# -------------------------

worlds = [
    "在一個科技與魔法並存的世界",
    "在人類已經移居外太空的未來殖民地",
    "在一個被AI統治的城市",
    "在戰爭後重建的廢土世界",
    "在一個隱藏於現代社會的地下世界"
]

conflicts = [
    "資源極度匱乏，各勢力爭奪生存空間",
    "人類與人工智慧之間爆發衝突",
    "古老勢力重新復甦並試圖掌控世界",
    "政府秘密實驗導致世界秩序崩壞",
    "不同陣營為了未知能源展開戰爭"
]

character_arcs = [
    "逐漸發現自己的過去被刻意隱藏",
    "在命運與自由之間掙扎",
    "被迫成為改變世界的關鍵人物",
    "從普通人逐漸成長為傳奇存在",
    "在追尋真相的過程中失去重要的人"
]

main_plots = [
    "踏上尋找真相的旅程",
    "被捲入一場跨勢力的陰謀",
    "必須保護一個關鍵的秘密",
    "與強大敵人展開生死對決",
    "試圖阻止即將毀滅世界的事件"
]


def generate_story(job, gender, height):
    world = random.choice(worlds)
    conflict = random.choice(conflicts)
    arc = random.choice(character_arcs)
    plot = random.choice(main_plots)

    character_story = (
        f"一名身高 {height} cm 的 {gender} {job}，"
        f"在成長過程中展現出與眾不同的能力，"
        f"並且 {arc}。"
    )

    world_background = f"{world}，{conflict}。"

    main_story = (
        f"{world}中，一名{job}因命運而被捲入事件，"
        f"他/她將{plot}，並在過程中改變整個世界的走向。"
    )

    return world_background, character_story, main_story

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

    result_story = None

    if request.method == "POST":

        job = request.form.get("job")
        gender = request.form.get("gender")
        height = request.form.get("height")

        # 🧠 Step 1：組 prompt（關鍵）
        prompt = f"""
你是一位小說作家，請根據以下角色設定，創作一段完整、連貫的短篇故事（只輸出一段，不要分段，不要標題）：

角色資訊：
- 職業：{job}
- 性別：{gender}
- 身高：{height} cm

要求：
- 必須有世界背景
- 必須有角色成長或衝突
- 必須有事件推進
- 風格偏奇幻或科幻敘事
- 長度約 200~300 字
"""

        try:
            # 🧠 Step 2：呼叫 OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一位專業小說作家"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9
            )

            result_story = response.choices[0].message.content

        except Exception as e:
            result_story = f"Error: {str(e)}"

    return render_template(
        "portfolio.html",
        story=result_story
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
