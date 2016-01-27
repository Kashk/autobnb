import datetime, json, logging, sys
import requests

logging.basicConfig(level=logging.DEBUG)

API_KEY = "915pw2pnf4h1aiguhph5gc5b2"  # same for everyone on mobile
#API_KEY = "d306zoyjsyarp7ifhu67rjxn52tv0t20"  # same for everyone on desktop

LISTING_IDS = {
    1: 5196399,
    2: 5253439,
    3: 5299538,
    4: 5299461,
    5: 8763366,
    6: 8763529,
    7: 8763407,
    8: 8763620
}


class AirbnbAPI:
    def __init__(self, username, password):
        self._session = requests.Session()

        self._session.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "X-Airbnb-API-Key": API_KEY,
            "User-Agent": "Airbnb/16.02 iPhone/9.2.1 Type/Phone"
        }

        login_payload = {"username": username,
                         "password": password,
                         "prevent_account_creation": "true"}

        r = self._session.post(
            "https://api.airbnb.com/v1/authorize", data=json.dumps(login_payload)
        )

        if "access_token" not in r.json():
            raise Exception("Error logging in: %s" % r.json())
        r.raise_for_status()

        self._access_token = r.json()["access_token"]

        self._session.headers.update({
            "X-Airbnb-OAuth-Token": self._access_token
        })

        r = self._session.get("https://api.airbnb.com/v1/account/active")
        r.raise_for_status()

        self.uid = r.json()["user"]["user"]["id"]

    def get_profile(self):
        r = self._session.get("https://api.airbnb.com/v1/users/%s" % self.uid)
        r.raise_for_status()

        return r.json()

    def get_calendar(self, listing_key):
        url = "https://api.airbnb.com/v2/calendars/" + \
            "{listing_id}/{start_date}/{end_date}?_format=host_calendar".format(
                listing_id=LISTING_IDS[listing_key],
                start_date=datetime.date.today(),
                end_date=datetime.date.today() + datetime.timedelta(days=7*4)
            )
        r = self._session.get(url)
        r.raise_for_status()
        return r.json()['calendar']['days']

    def get_reservations(self, listing_key):
        days = self.get_calendar(listing_key)
        resos = {}
        for day in days:
            if not day["reservation"]: continue
            date = datetime.datetime.strptime(day["date"], "%Y-%m-%d").date()
            res_id = day["reservation"]["confirmation_code"]
            if res_id not in resos:
                start_date = datetime.datetime.strptime(day["reservation"]["start_date"], "%Y-%m-%d").date()
                resos[res_id] = {
                    "guest": day["reservation"]["guest"],
                    "start_date": start_date,
                    "end_date": start_date + datetime.timedelta(days=day["reservation"]["nights"]),
                }
        return resos

if __name__ == '__main__':
    import django
    django.setup()

    airbnb = AirbnbAPI("zain@inzain.net", "0v*8HrG*&D25EyXP")
    resos = airbnb.get_reservations(4)

    from guests.models import Reservation

    for confirmation_code, reso in resos.items():
        if not Reservation.objects.filter(confirmation_code=confirmation_code).exists():
            Reservation.objects.create(
                confirmation_code=confirmation_code, dates=(reso["start_date"], reso["end_date"]), guest=reso['guest'])
