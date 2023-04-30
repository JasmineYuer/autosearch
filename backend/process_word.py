import re
from threading import Lock, Thread
import time
import pandas as pd
from backend import utils

mutex = Lock()


def get_word_from_path(word_path):
    with open(word_path, "r", encoding="utf-8") as f:
        word = f.read()

    word = list(
        set([i.replace("\xa0", " ").replace("\u202f", " ") for i in word.split("\n")])
    )
    return word


def find_word_in_txt(
    word, file_name, above=1, below=1, ignore_case=True, exact_match=True
):
    with open(file_name, "r", encoding="utf-8") as f:
        txt = f.read()

    if exact_match:
        p = f"\\b{word}\\b"
    else:
        p = word
    if ignore_case:
        pattern = re.compile(p, re.IGNORECASE)
    else:
        pattern = re.compile(p)

    line_idx = []
    for i, line in enumerate(txt.splitlines()):
        if re.search(pattern, line):
            if i == 0:
                start = 0
                end = below + 1
            elif i == len(txt.splitlines()) - 1:
                start = start = max(i - above, 0)
                end = len(txt.splitlines()) - 1
            else:
                start = max(i - above, 0)
                end = min(i + below + 1, len(txt.splitlines()) - 1)
            line_idx += list(range(start, end))
    line_idx = list(set(line_idx))
    final = ""
    for idx in range(len(line_idx)):
        if idx == 0:
            pre = 0
        else:
            pre = line_idx[idx - 1]

        cur = line_idx[idx]

        if cur - pre > 1:
            final += "\n\n\n"

        final += txt.splitlines()[cur] + "\n"
    return final


#     return result


def run_search(
    file_lk_map, word_lst, above=2, below=2, ignore_case=True, exact_match=True
):
    final = []
    for file, link in file_lk_map.items():
        for w in word_lst:
            search = find_word_in_txt(
                w,
                file,
                above=above,
                below=below,
                ignore_case=ignore_case,
                exact_match=exact_match,
            )
            if search == "":
                pass
            else:
                final.append([file, link, w, search])
        print(file, "finished!")
    df = pd.DataFrame(final, columns=["file", "link", "word", "content"])
    utils.df_to_xlsx(df, "./result/result.xlsx")
    # df.to_excel("./result/result.xlsx", sheet_name="search_result", index=False)
