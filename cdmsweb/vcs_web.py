from flask import Blueprint, jsonify, abort, url_for, request, g, Response
import vcs
import tempfile


vcsweb = Blueprint("vcs", __name__)


def named(base_route):
    route = base_route + "/<name>"
    defaults = {"name": "default"}

    def dec(func):
        return vcsweb.route(base_route, defaults=defaults)(vcsweb.route(route)(func))
    return dec


@named("/boxfill")
def boxfill(name):
    try:
        box = vcs.getboxfill(name)
    except:
        abort(404)
    box_dict, _ = vcs.utils.dumpToDict(box)
    box = {}
    for k, v in box_dict.iteritems():
        if v == 1e20:
            v = None
        box[k] = v
    return jsonify(box)


@vcsweb.route("/boxfill/<name>/levels")
def boxfill_levels(name):
    try:
        box = vcs.getboxfill(str(name))
    except:
        abort(404)
    minimum, maximum = float(request.args.get("min", 0)), float(request.args.get("max", 0))
    levs = box.getlevels(minimum, maximum).tolist()
    return jsonify(levs)


@vcsweb.route("/utils/colors")
def get_colors():
    levs = [float(l) for l in request.args.get("levels").split(",")]
    return jsonify(vcs.utils.getcolors(levs))


@named("/colormap")
def colormap(name):
    try:
        cmap = vcs.getcolormap(name)
    except:
        abort(404)
    cmap_dict, _ = vcs.utils.dumpToDict(cmap)
    return jsonify(cmap_dict)


@named("/isofill")
def isofill(name):
    try:
        iso = vcs.getisofill(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(iso)[0])


@named("/isoline")
def isoline(name):
    try:
        gm = vcs.getisoline(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/marker")
def marker(name):
    try:
        gm = vcs.getmarker(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/vector")
def vector(name):
    try:
        gm = vcs.getvector(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/meshfill")
def meshfill(name):
    try:
        gm = vcs.getmeshfill(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/projection")
def projection(name):
    try:
        obj = vcs.getprojection(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/texttable")
def texttable(name):
    try:
        obj = vcs.gettexttable(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/textorientation")
def textorientation(name):
    try:
        obj = vcs.gettextorientation(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/textcombined")
def textcombined(name):
    try:
        obj = vcs.gettextcombined(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/line")
def line(name):
    try:
        obj = vcs.getline(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/fillarea")
def fillarea(name):
    try:
        obj = vcs.getfillarea(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/font")
def font(name):
    try:
        obj = vcs.getfont(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/3d_scalar")
def scalar_3d(name):
    try:
        obj = vcs.get3d_scalar(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/3d_dual_scalar")
def dual_scalar_3d(name):
    try:
        obj = vcs.get3d_dual_scalar(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/3d_vector")
def vector_3d(name):
    try:
        obj = vcs.get3d_vector(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/template")
def template(name):
    try:
        obj = vcs.gettemplate(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/taylordiagram")
def taylordiagram(name):
    try:
        obj = vcs.gettaylordiagram(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/1d")
def oned(name):
    try:
        obj = vcs.get1d(name)
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(vcsweb, url_prefix="/vcs")
    app.run()
