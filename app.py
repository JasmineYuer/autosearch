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


# @app.route("/", methods=["GET", "POST"])
# def upload_file():
#     if request.method == "POST":
#         print(request.files, request.form)
#         wordtxt = request.files["wordtxt"]
#         linktxt = request.files["linktxt"]
#         case = True if request.form["case"] == "True" else False
#         exact = True if request.form["exact"] == "True" else False
#         above = int(request.form["above"])
#         below = int(request.form["below"])
#         deep_dive = True if request.form["deep_dive"] == "True" else False
#         level = int(request.form["level"])
#         stimeout = int(request.form["stimeout"])

#         if wordtxt.filename == "" or linktxt.filename == "":
#             flash("Please upload both word.txt and link.txt")
#             return redirect(request.url)

#         if wordtxt and allowed_file(wordtxt.filename):
#             filename = secure_filename(wordtxt.filename)
#             wordtxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
#             word = pw.get_word_from_path(
#                 os.path.join(app.config["UPLOAD_FOLDER"], filename)
#             )

#         if linktxt and allowed_file(linktxt.filename):
#             filename = secure_filename(linktxt.filename)
#             linktxt.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
#             link = pl.get_link_from_path(
#                 os.path.join(app.config["UPLOAD_FOLDER"], filename)
#             )

#         file_lk_map, fail_map = pl.write_to_files(link, timeout=stimeout)
#         print("finish parse")
#         final, lk_no_hit = pw.run_search(
#             file_lk_map,
#             word,
#             above=above,
#             below=below,
#             ignore_case=case,
#             exact_match=exact,
#         )

#         df = pd.DataFrame(final, columns=["link", "word", "content"])
#         utils.df_to_xlsx(df, "./result/result.xlsx")

#         summary = []
#         for l in link:
#             if l in fail_map:
#                 summary.append([l, fail_map[l]])
#             elif l in lk_no_hit:
#                 summary.append([l, "no hit"])
#             else:
#                 summary.append([l, "hit"])
#         summary = pd.DataFrame(summary, columns=["Link", "Result"])
#         with pd.ExcelWriter(
#             "./result/result.xlsx", engine="openpyxl", mode="a"
#         ) as writer:
#             summary.to_excel(writer, sheet_name="summary")

#         filename = "result.xlsx"
#         finish = True
#         return render_template("upload.html", finish=finish, filename=filename)
#     return render_template("upload.html")


@app.route("/", methods=["GET", "POST"])
def link_to_text():
    finish = False
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

        file_lk_map, fail_map = pl.write_to_files(link, timeout=stimeout)
        utils.zip_files()
        filename = "link_result.zip"
        print("finish parse", file_lk_map)
        finish = True
        return render_template("link.html", finish=finish, filename=filename)

    return render_template("link.html", finish=finish)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    print(os.path.join("result", filename))
    return send_from_directory("./result", filename)


@app.route("/search_word")
def search_word():
    return "hello world"


if __name__ == "__main__":
    app.run()
