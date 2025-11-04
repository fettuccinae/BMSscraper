from flask import (
    Blueprint,
    url_for,
    request,
    flash,
    current_app,
    render_template,
    g,
    redirect,
    jsonify,
)
import re
import json
import threading
from webserver.decorators import login_required
from webserver.db.user import (
    add_new_notification_event,
    get_user_notifications,
    add_notification_detail,
    i_run_through_them_all,
    update_notifications,
    get_notifications_by_rem_ids,
)
from webserver.scrape.scraper import scrape
from webserver.mail import send_mail, cron_job_mail_sending

tix_bp = Blueprint("tix", __name__)


@tix_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_event():
    if request.method == "POST":
        url = request.form.get("scrape_url")
        option = request.form.get("scrape_option")
        frequency = request.form.get("frequency")
        # from_ts = _convert_string_time_to_int(request.form.get("from_time"))
        # to_ts = _convert_string_time_to_int(request.form.get("till_time"))

        if not url or not option or not frequency:
            flash("Please select errthing")

        elif option not in ("tickets", "movie"):
            flash("what the helli")

        else:
            try:
                notification = add_new_notification_event(g.user["id"], url, option, frequency)

                # too lazy to think here.
                if notification["scrape_option"] == "tickets":
                    detail = scrape([(None, notification["scrape_url"])], None)
                else:
                    detail = scrape(None, [(None, notification["scrape_url"])])

                add_notification_detail(notification["rem_id"], detail)

                # life saving condition lmao.
                if detail.get("available") is True:
                    name = re.search(r"(.*\/((vijayawada\/)|(hyderabad\/)))([^\/]+)(\/.*)", url).group(5)
                    send_mail(
                        f"Update for {name} in BMS", json.dumps(detail), notification["mail_id"]
                    )
                else:
                    current_app.logger.info("NOT YET BRO")

                flash("When its available, A mail will be sent on your mail id")

                return redirect(url_for("tix.index"))
            except Exception as err:
                flash("SOME ERROR SHAW")
                current_app.logger.error(err)

    return render_template("tix/add_event.html")


@tix_bp.get("/")
@login_required
def index():
    all_notifications = get_user_notifications(g.user["id"])
    return render_template("tix/index.html", notifications=all_notifications)


@tix_bp.get("/wake-up")
def wake_up():
    return jsonify({"status": "up"})

@tix_bp.get("/cron-jobs")
def cron():
    secret = request.args.get("secret")
    if not secret or secret != current_app.config["CRON_SECRET"]:
        return jsonify({"status": "nah"}), 401
    else:
        hemdilla = i_run_through_them_all(request.args.get("frequency"))
        if not hemdilla:
            return jsonify({"status": "aight"})
        # this was sending empty lists everywhere around till like the last one. phew
        tix_urls = []
        movie_urls = []
        current_app.logger.info(hemdilla)
        for u in hemdilla:
            if u["scrape_option"] == "movie":
                movie_urls.append((u["rem_id"], u["scrape_url"]))
            else:
                tix_urls.append((u["rem_id"], u["scrape_url"]))
        print(tix_urls)
        print(movie_urls)


        app = current_app._get_current_object()
        def run_the_slow_part_in_context(tix_urls, movie_urls):
            with app.app_context():
                _the_slow_part(tix_urls, movie_urls)

        thread = threading.Thread(target=run_the_slow_part_in_context, args=(tix_urls, movie_urls))
        thread.start()

        return jsonify({"status": "aight"})

def _the_slow_part(tix_urls, movie_urls):
        
        new_shit_1, new_shit_2 = scrape(tix_urls, movie_urls)
        print(new_shit_1)
        print(new_shit_2)
        
        rem_ids_for_updated_ones = update_notifications(new_shit_1, new_shit_2)
        mailing_data = get_notifications_by_rem_ids(rem_ids_for_updated_ones)
        cron_job_mail_sending(mailing_data)


def _convert_string_time_to_int(time: str) -> int:
    return int(time[:2] + time[3:])


def run_hourly_job():
    current_app.logger.info("HELLO")
