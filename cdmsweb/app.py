from flask import Flask, render_template
from cdms_web import serve_dir
from vcs_web import serve_vcs
import vcs

app = Flask(__name__)

serve_dir(app, vcs.sample_data)
serve_vcs(app)


@app.route("/boxfill/<filename>/<varname>")
def general_boxfill(filename, varname):
    return render_template("box.html", data_url="/sample_data/%s/%s/meta" % (filename, varname), boxfill_name="a_boxfill")


@app.route("/clt_boxfill")
def clt_boxfill():
    return render_template("box.html", data_url="/sample_data/clt.nc/clt/meta", boxfill_name="a_boxfill")

@app.route("/navy_boxfill")
def navy_boxfill():
    return render_template("box.html", data_url="/sample_data/navy_land.nc/sftlf/meta", boxfill_name="default")

if __name__ == "__main__":
    app.run()
