import os

from flask import Flask, render_template
from flask_wtf import CSRFProtect

from strava_viewer.strava.services.activities_services import get_club_activities

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

STRAVA_CLUB_ID = os.getenv("STRAVA_CLUB_ID")


@app.route("/")
@app.route("/index")
def index():
    club_activities = get_club_activities(STRAVA_CLUB_ID)
    return render_template("index.html", club_activities=club_activities)


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
