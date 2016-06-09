from flask import Blueprint, jsonify, abort, url_for, request, g, Response
import vcs
import os


vcsweb = Blueprint("vcs", __name__)


def named(base_route, default="default"):
    route = base_route + "/<name>"
    defaults = {"name": default}

    def dec(func):
        return vcsweb.route(base_route, defaults=defaults)(vcsweb.route(route)(func))
    return dec


@named("/continents", default="data_continent_fine")
def continents(name):
    fnm = os.path.join(vcs.prefix, "share", "vcs", name)

    f = open(fnm)
    ln = f.readline()

    lines = []
    while ln.strip().split() != ["-99", "-99"]:
        pts = []
        # Many lines, need to know number of points
        N = int(ln.split()[0])
        # Now create and store these points
        n = 0
        while n < N:
            ln = f.readline()
            sp = ln.split()
            sn = len(sp)
            didIt = False
            if sn % 2 == 0:
                try:
                    spts = []
                    for i in range(sn / 2):
                        l, L = float(sp[i * 2]), float(sp[i * 2 + 1])
                        spts.append([l, L])
                    for p in spts:
                        pts.append([p[1], p[0]])
                    n += sn
                    didIt = True
                except:
                    didIt = False
            if didIt is False:
                while len(ln) > 2:
                    l, L = float(ln[:8]), float(ln[8:16])
                    pts.append([L, l])
                    ln = ln[16:]
                    n += 2
        lines.append(pts)
        ln = f.readline()
    return jsonify(lines)


@named("/boxfill")
def boxfill(name):
    try:
        box = vcs.getboxfill(str(name))
    except:
        abort(404)
    box_dict, _ = vcs.utils.dumpToDict(box)
    box = {}
    for k, v in box_dict.iteritems():
        if v == 1e20:
            v = None
        if isinstance(v, (list, tuple)):
            new_v = []
            for val in v:
                if val == 1e20:
                    new_v.append(None)
                else:
                    new_v.append(val)
            v = new_v
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
        cmap = vcs.getcolormap(str(name))
    except:
        abort(404)
    cmap_dict, _ = vcs.utils.dumpToDict(cmap)
    return jsonify(cmap_dict)


@named("/isofill")
def isofill(name):
    try:
        iso = vcs.getisofill(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(iso)[0])


@named("/isoline")
def isoline(name):
    try:
        gm = vcs.getisoline(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/marker")
def marker(name):
    try:
        gm = vcs.getmarker(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/vector")
def vector(name):
    try:
        gm = vcs.getvector(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/meshfill")
def meshfill(name):
    try:
        gm = vcs.getmeshfill(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(gm)[0])


@named("/projection")
def projection(name):
    try:
        obj = vcs.getprojection(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/texttable")
def texttable(name):
    try:
        obj = vcs.gettexttable(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/textorientation")
def textorientation(name):
    try:
        obj = vcs.gettextorientation(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/textcombined")
def textcombined(name):
    try:
        obj = vcs.gettextcombined(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/line")
def line(name):
    try:
        obj = vcs.getline(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/fillarea")
def fillarea(name):
    try:
        obj = vcs.getfillarea(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/font")
def font(name):
    try:
        obj = vcs.getfont(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/3d_scalar")
def scalar_3d(name):
    try:
        obj = vcs.get3d_scalar(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/3d_dual_scalar")
def dual_scalar_3d(name):
    try:
        obj = vcs.get3d_dual_scalar(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/3d_vector")
def vector_3d(name):
    try:
        obj = vcs.get3d_vector(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/template")
def template(name):
    try:
        obj = vcs.gettemplate(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/taylordiagram")
def taylordiagram(name):
    try:
        obj = vcs.gettaylordiagram(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


@named("/1d")
def oned(name):
    try:
        obj = vcs.get1d(str(name))
    except:
        abort(404)
    return jsonify(vcs.utils.dumpToDict(obj)[0])


def serve_vcs(app):
    app.register_blueprint(vcsweb, url_prefix="/vcs")

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    serve_vcs(app)
    app.run()
