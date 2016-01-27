import datetime, json, logging, sys
from django.conf import settings
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
                start_date=datetime.date.today() - datetime.timedelta(days=7),
                end_date=datetime.date.today() + datetime.timedelta(days=7*2)
            )
        r = self._session.get(url)
        r.raise_for_status()
        return r.json()['calendar']['days']

    def get_reservations_from_calendar(self, listing_key):
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
                    "thread_id": None,  # gets added in get_all_reservations
                }
        return resos

    def get_all_reservations(self):
        all_resos = {}
        for listing_key in LISTING_IDS.keys():
            resos = self.get_reservations_from_calendar(listing_key)
            all_resos.update(resos)

        ## associate resos with thread_ids
        payload = {
            '_order': 'start_date',
            '_limit': 50,
            'start_date': datetime.date.today() - datetime.timedelta(days=7),
            'end_date': datetime.date.today() + datetime.timedelta(days=7*2),
            '_format': 'host_dashboard_mobile',
            '_offset': 0,
            'host_id': self.uid,
        }

        r = self._session.get('https://api.airbnb.com/v2/reservations', params=payload)
        r.raise_for_status()

        for reso in r.json()['reservations']:
            if reso['confirmation_code'] in all_resos:
                all_resos[reso['confirmation_code']]['thread_id'] = reso['thread_id']

        return all_resos

    def send_message(self, thread_id, message):
        payload = {
            'message': message,
            'thread_id': thread_id,
        }

        r = self._session.post('https://api.airbnb.com/v2/messages', data=json.dumps(payload))
        r.raise_for_status()
