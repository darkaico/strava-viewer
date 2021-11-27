import os

from flask import Flask, render_template

from strava_extensions.strava.api import StravaAPI

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    token = os.getenv("STRAVA_API_ACCESS_TOKEN")
    club_id = os.getenv("STRAVA_CLUB_ID")

    strava_api = StravaAPI(token)
    club_activities = strava_api.get_club_activities(club_id)

    return render_template("index.html", club_activities=club_activities)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
