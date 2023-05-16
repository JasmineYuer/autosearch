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
    utils.create_result_folder("pickles")
    return render_template("home.html")


# additional variable
# log system
# dev and prod pod
@app.route("/deep_search", methods=["GET", "POST"])
def deep_search():
    if request.method == "POST":
        linktxt = request.files["linktxt"]
        linkarea = request.form["linkarea"]
        # assert check
        stimeout = int(request.form["stimeout"])
        level = int(request.form["level"])
        if linktxt and allowed_file(linktxt.filename):
            filename = secure_filename(linktxt.filename)
            linktxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            link = pl.get_link_from_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
        else:
            link = [
                i.replace("\xa0", " ").replace("\r", "")
                for i in linkarea.split("\n")
                if i != ""
            ]
        final_link = []
        fail_link = []
        irr_link = []
        utils.create_result_folder("deep_link")

        for url in link:
            lks, fail_lks, irr_lks = pl.url_deepdive(url, level, stimeout)
            final_link += lks
            fail_link += fail_lks
            irr_link += irr_lks
        with open("./deep_link/deeplink.txt", "w", encoding="utf-8") as f:
            txt = "\n".join(final_link)
            f.write(txt)
        with open("./deep_link/deeplink_fail.txt", "w", encoding="utf-8") as f:
            txt = "\n".join(fail_link)
            f.write(txt)
        with open("./deep_link/deeplink_irrelevant.txt", "w", encoding="utf-8") as f:
            txt = "\n".join(irr_link)
            f.write(txt)
        utils.zip_txt_files("deep_link", "deep_search.zip")
        session["source"] = "deep_link"
        session["filename"] = {"deep_search": "deep_search.zip"}
        return redirect("/result")
    return render_template("deeplink.html")


@app.route("/search_link", methods=["GET", "POST"])
def link_to_text():
    if request.method == "POST":
        session["source"] = "link"
        linktxt = request.files["linktxt"]
        linkarea = request.form["linkarea"]
        # assert check
        stimeout = int(request.form["stimeout"])
        if linktxt and allowed_file(linktxt.filename):
            filename = secure_filename(linktxt.filename)
            linktxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            link = pl.get_link_from_path(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
        else:
            link = [
                i.replace("\xa0", " ").replace("\r", "")
                for i in linkarea.split("\n")
                if i != ""
            ]
            print(link)

        file_lk_map, fail_map = pl.write_to_files(link, timeout=stimeout)
        utils.store_var(file_lk_map, "file_lk_map")
        utils.store_var(fail_map, "fail_map")
        utils.store_var(link, "link")

        utils.zip_txt_files("result", "link_result.zip")
        session["filename"] = {"link": "link_result.zip"}
        return redirect("/result")
    return render_template("link.html")


@app.route("/search_word", methods=["GET", "POST"])
def search_word():
    print(request.method)
    if request.method == "POST":
        wordtxt = request.files["wordtxt"]
        wordarea = request.form["wordarea"]
        # assert check needed
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
                        i.replace("\xa0", " ").replace("\u202f", " ").replace("\r", "")
                        for i in wordarea.split("\n")
                    ]
                )
            )
        case = True if request.form["case"] == "True" else False
        exact = True if request.form["exact"] == "True" else False
        above = int(request.form["above"])
        below = int(request.form["below"])

        file_lk_map = utils.get_var("file_lk_map")
        file_lk_map_reverse = utils.back_search(file_lk_map)
        fail_map = utils.get_var("fail_map")
        link = utils.get_var("link")
        print(file_lk_map_reverse)
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
                summary.append([l, fail_map[l], None])
            elif l in lk_no_hit:
                summary.append([l, "no hit", file_lk_map_reverse[l]])
            else:
                summary.append([l, "hit", file_lk_map_reverse[l]])
        summary = pd.DataFrame(summary, columns=["Link", "Result", "File"])
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
    print(session["source"])
    if session["source"] == "deep_link":
        session["folder"] = "deep_link"
    else:
        session["folder"] = "result"
    return render_template(
        "result.html", filename=session["filename"], source=session["source"]
    )


@app.route("/download/<filename>")
def download_file(filename):
    folder = session["folder"]
    return send_from_directory(f"./{folder}", filename)


if __name__ == "__main__":
    app.run(debug=True)
