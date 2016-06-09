from flask import Blueprint, jsonify, abort, url_for, request, g, Response
import cdms2
import os
import numpy
import urllib


cdmsweb = Blueprint("cdms", __name__)


@cdmsweb.url_defaults
def url_defaults(endpoint, values):
    root_path = getattr(g, 'root_path', None)
    if root_path is not None:
        values.setdefault('root_path', root_path)


@cdmsweb.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.root_path = values.pop('root_path')


@cdmsweb.route("/files")
def files():
    urls = []
    for f in os.listdir(g.root_path):
        if f[0] == ".":
            continue
        urls.append(url_for('.file_vars', fname=f))
    return jsonify(urls)


@cdmsweb.route("/<fname>/variables")
def file_vars(fname):
    path = os.path.join(g.root_path, fname)
    if not os.path.exists(path):
        abort(404)

    f = cdms2.open(path)

    var_urls = []
    for v in f.variables.keys():
        var_urls.append(url_for('.var_meta', fname=fname, var_id=v))

    f.close()
    return jsonify(var_urls)


@cdmsweb.route("/<fname>/<var_id>/meta")
def var_meta(fname, var_id):
    path = os.path.join(g.root_path, fname)
    if not os.path.exists(path):
        abort(404)

    f = cdms2.open(path)

    if var_id not in f.variables:
        abort(404)

    v = f[var_id]
    axis_links = [url_for('.var_axis', fname=fname, var_id=var_id, axis=a) for a in v.getAxisIds()]
    var_link = url_for('.var', fname=fname, var_id=var_id)

    f.close()
    return jsonify({"variable": var_link, "axes": axis_links})


@cdmsweb.route("/<fname>/<var_id>/<axis>")
def var_axis(fname, var_id, axis):
    path = os.path.join(g.root_path, fname)
    if not os.path.exists(path):
        abort(404)

    f = cdms2.open(path)

    if var_id not in f.variables:
        abort(404)

    v = f[var_id]

    if axis not in v.getAxisIds():
        abort(404)

    a = v.getAxis(v.getAxisIndex(a))

    axis_desc = {}
    bounds = axis.getBounds()
    if bounds is not None:
        axis_desc["bounds"] = bounds.tolist()

    values = axis.getData().tolist()
    axis_desc["data"] = values
    axis_desc["attributes"] = {}
    for attr, value in a.attributes().iteritems():
        if isinstance(value, numpy.ndarray):
            value = value.tolist()
        axis_desc["attributes"][attr] = value
    f.close()
    return jsonify(axis_desc)


@cdmsweb.route("/<fname>/<var_id>/array")
def var(fname, var_id):
    path = os.path.join(g.root_path, fname)
    if not os.path.exists(path):
        abort(404)

    f = cdms2.open(path)

    if var_id not in f.variables:
        abort(404)

    v = f[var_id]
    axes = v.getAxisIds()
    axis_args = {}
    for arg, value in request.args.iteritems():
        if arg in axes:
            vals = value.split(",")
            values = []
            for val in vals:
                try:
                    val = float(val)
                except ValueError:
                    val = str(val)
                values.append(val)
            if len(values) == 1:
                values = values[0]
            axis_args[arg] = values
            print values
    transient = v(squeeze=True, **axis_args)
    flat = transient.flatten()
    data_type = flat.dtype
    shape = transient.shape
    resp = Response(response=flat.tobytes(), status=200)
    resp.headers["x-cdms-datatype"] = data_type.name
    resp.headers["x-cdms-shape"] = shape
    return resp


def serve_dir(app, path, url_prefix=None):
    """
    Provides cdmsweb functionality to the specified path.

    @param app: Flask app to bind to
    @param path: Path to serve
    @param url_prefix: Optional, prefix to bind path at.
                       Will use URL encoded basename if none provided.
    """
    if url_prefix is None:
        dir_name = os.path.split(path)[-1]
        url_prefix = "/" + urllib.quote(dir_name)
    app.register_blueprint(cdmsweb, url_prefix=url_prefix, url_defaults={"root_path": path})

if __name__ == "__main__":
    from flask import Flask
    import vcs
    app = Flask(__name__)
    serve_dir(app, vcs.sample_data)
    serve_dir(app, "/Users/fries2/Desktop/el nino", url_prefix="/el_nino")
    app.run()
