

import functools
import io
import os
import pathlib as p
import re
import traceback
import zipfile as zf

from flask import Flask, Response, redirect



zip_dic = {}


def load_one_zip(zip_path, zip_file):

    print("Download: processing", zip_file)

    with open(zip_path / zip_file, 'rb') as f:

        contents = f.read()

    nv_opt = decode(zip_file)

    if nv_opt is not None:
        n, v = nv_opt
        return [n, v, io.BytesIO(contents)]
    else:
        return None


def load_all_zips():

    global zip_dic

    zip_file_path = p.Path(os.getcwd()) / "static" / "zips"
    zip_file_names = os.listdir(zip_file_path)

    doc_files = [nvc
                 for zip_file_name in zip_file_names
                 for nvc in [load_one_zip(zip_file_path, zip_file_name)]
                 if nvc is not None
                 ]

    def fold_fct(n_dict, nvc):
        (n, v, c) = nvc
        v_dict = n_dict.get(n, {})
        v_dict[v] = c
        n_dict[n] = v_dict
        return n_dict

    zip_dic = functools.reduce(fold_fct, doc_files, {})



def decode(str):

    pat = "([a-z_]+)-(\d+\.\d+\.\d+).zip"

    m = re.match(pat, str)

    if m is None:
        return None
    else:
        return (m[1], m[2])


def scan_entries():

    ns = sorted(list(zip_dic.keys()))

    entries = [{"name": n,
                "versions": sorted(zip_dic[n].keys())
                }
               for n in ns
               ]

    return entries

app = Flask(__name__)

@app.route("/entries")
def entries_handler():

    r = scan_entries()
    return r


def get_file(package, version, path, mode='r'):

    if package in zip_dic:
        if version in zip_dic[package]:

            contents = zip_dic[package][version]

            z = zf.ZipFile(contents, 'r')

            with z.open(str(path), mode=mode) as f:
                return f.read()
        else:
            return "No Version Found"
    else:
        return "No Package Found"



@app.route('/docs/<package>/<version>/html/<fn>')
def doc_1_handler(package, version, fn):
    resp = get_file(package, version, p.Path("html") / fn, "r")
    return resp


@app.route('/docs/<package>/<version>/html/_static/<fn>')
def doc_2_handler(package, version, fn):

    resp = get_file(package, version, p.Path("html/_static") / fn, "r")
    return resp


@app.route('/docs/<package>/<version>/html/_static/css/<fn>')
def doc_3_handler(package, version, fn):

    str = get_file(package, version, p.Path("html/_static") / "css" / fn, "r")
    resp = Response(str)
    resp.headers['Content-Type'] = 'text/css; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/docs/<package>/<version>/html/_static/js/<fn>')
def doc_4_handler(package, version, fn):

    str = get_file(package, version, p.Path("html/_static") / "js" / fn, "r")
    resp = Response(str)
    resp.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/docs/<package>/<version>/html/_static/css/fonts/<fn>')
def doc_5_handler(package, version, fn):

    str = get_file(package, version, p.Path("html/_static") / "css" / 'fonts' / fn, "r")
    resp = Response(str)
    resp.headers['Content-Type'] = 'font/woff2'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route('/docs/<package>/<version>/html/_sources/<fn>')
def doc_6_handler(package, version, fn):

    str = get_file(package, version, p.Path("html/_sources") / fn, "r")
    resp = Response(str)
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@app.route("/reload")
def reload_handler():
    global zip_dic

    print("Reloading")
    zip_dic = {}
    load_all_zips()
    print("Reloading Done")
    return {}


@app.route('/')
def reroute_handler():
    return redirect("/static/index.html", code=302)


if __name__ == '__main__':

    load_all_zips()

    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
