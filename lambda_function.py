import json
import re
import os
import requests
import datastore


def show(d: dict, limit: int = 1000):
    footer_url = "https://hamukazu.github.io/kaldi_sale_info/#Tokyo\n"
    s = ""
    if len(d) == 0:
        s += "セール情報はありません。\n"
    else:
        for x in d:
            ss = x["shop"]
            ss += "："
            ss += x["title"]
            ss += "\n"
            ss += "  "
            if x["include_now"]:
                ss += "【現在開催中】"
            ss += x["date"]
            ss += "\n"
            if len(s) + len(ss) + len(footer_url) + 6 < limit:
                s += ss
            else:
                s += "...他\n"
                break
        s += "\n"
    s += footer_url

    return s


def equal(a, b):
    c = int(a is None) + int(b is None)
    if c == 1:
        return False
    elif c == 2:
        return True
    else:
        sort_key = lambda x: x["shop"]
        a_sorted = sorted(a, key=sort_key)
        b_sorted = sorted(b, key=sort_key)
        return a_sorted == b_sorted


def lambda_handler(event, context):
    webhook_url = os.environ["WEBHOOK_URL"]
    key = os.environ["KEY"]
    dry_run = int(os.environ.get("DRY_RUN", 0))
    no_save = int(os.environ.get("NO_SAVE", 0))
    with open("favorites.txt", "r") as f:
        favorites = f.read().splitlines()

    store = datastore.store("Tokyo.json").get()
    sale = [] if store is None else json.loads(store)
    d = [x for x in sale if x["shop"] in favorites]
    store2 = datastore.store(f"{key}.json")
    st2 = store2.get()
    d_prev = None if st2 is None else json.loads(st2)
    if not equal(d, d_prev):
        post = show(d)
        if dry_run:
            print(post)
        else:
            payload = {
                "content": post,
                "username": "カルディセール情報bot"
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        if not no_save:
            store2.put(json.dumps(d))


if __name__ == "__main__":
    lambda_handler(None, None)
