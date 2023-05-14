import os
import pandas as pd
from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    send_from_directory,
    session,
)
from werkzeug.utils import secure_filename
from backend import process_link as pl
from backend import process_word as pw
from backend import utils

UPLOAD_FOLDER = "./test"
ALLOWED_EXTENSIONS = {"txt"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/deep_search", methods=["GET", "POST"])
def deep_search():
    return render_template("deeplink.html")


@app.route("/search_link", methods=["GET", "POST"])
def link_to_text():
    if request.method == "POST":
        linktxt = request.files["linktxt"]
        linkarea = request.form["linkarea"]
        stimeout = int(request.form["stimeout"])
        # assert (linktxt.filename == "") + (
        #     linkarea == ""
        # ) == 1, "Either upload or put some text"

        print(linktxt, linkarea, stimeout)
        if linktxt and allowed_file(linktxt.filename):
            filename = secure_filename(linktxt.filename)
            linktxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            link = pl.get_link_from_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
        else:
            link = [i.replace("\xa0", " ") for i in linkarea.split("\n") if i != ""]
            print(link)

        file_lk_map, fail_map = pl.write_to_files(link, timeout=stimeout)
        session["file_lk_map"] = file_lk_map
        session["fail_map"] = fail_map
        session["link"] = link
        utils.zip_files()
        session["filename"] = {"link": "link_result.zip"}
        session["source"] = "link"
        return redirect("/result")
    return render_template("link.html")


@app.route("/search_word", methods=["GET", "POST"])
def search_word():
    print(request.method)
    if request.method == "POST":
        print(request.files, request.form)
        wordtxt = request.files["wordtxt"]
        wordarea = request.form["wordarea"]
        if wordtxt and allowed_file(wordtxt.filename):
            filename = secure_filename(wordtxt.filename)
            wordtxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            word = pw.get_word_from_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
        else:
            word = list(
                set(
                    [
                        i.replace("\xa0", " ").replace("\u202f", " ")
                        for i in wordarea.split("\n")
                    ]
                )
            )
        case = True if request.form["case"] == "True" else False
        exact = True if request.form["exact"] == "True" else False
        above = int(request.form["above"])
        below = int(request.form["below"])

        file_lk_map = session["file_lk_map"]
        fail_map = session["fail_map"]
        link = session["link"]
        final, lk_no_hit = pw.run_search(
            file_lk_map,
            word,
            above=above,
            below=below,
            ignore_case=case,
            exact_match=exact,
        )

        df = pd.DataFrame(final, columns=["link", "word", "content"])
        utils.df_to_xlsx(df, "./result/result.xlsx")

        summary = []
        for l in link:
            if l in fail_map:
                summary.append([l, fail_map[l]])
            elif l in lk_no_hit:
                summary.append([l, "no hit"])
            else:
                summary.append([l, "hit"])
        summary = pd.DataFrame(summary, columns=["Link", "Result"])
        with pd.ExcelWriter(
            "./result/result.xlsx", engine="openpyxl", mode="a"
        ) as writer:
            summary.to_excel(writer, sheet_name="summary")

        session["filename"].update({"result": "result.xlsx"})
        session["source"] = "word"
        return redirect("/result")
    return render_template("word.html")


@app.route("/result")
def result_page():
    return render_template(
        "result.html", filename=session["filename"], source=session["source"]
    )


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("./result", filename)


if __name__ == "__main__":
    app.run()
