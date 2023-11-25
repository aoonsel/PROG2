
from flask import Flask, render_template, request



app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/overview")
def overview():


    return render_template(
        "overview.html",

    )


@app.route("/structure")
def structure():
    return render_template(
        "structure.html",

    )


@app.route("/courses")
def courses():
    return render_template(
        "courses.html",
    
    )



if __name__ == "__main__":
    app.run(debug=True)
