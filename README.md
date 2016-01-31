**autobnb cheat sheet**

run local dev server
$ heroku local:run python3 manage.py runserver

reservations staying today that you can test with:
[<Reservation: B24KRD - Jeffrey Lin>, <Reservation: 44Y9F8 - Ruben Parham>, <Reservation: Q5JNW3 - Akiko Tanaka>, <Reservation: 85WE8D - Bo Zimmerman>, <Reservation: SEYR9A - Robert S. Ramirez>, <Reservation: 8SWDN4 - Daniel Fagnan>]

http://127.0.0.1:8000/reso/<<confirmation code>>

files to edit: autobnb/chat/templates/reso.html, autobnb/chat/static/css/main.css


you probably won’t need the following, but just in case…

run migrations (if any)
$ heroku local:run python3 manage.py migrate

fetch reservations from airbnb and save to db
$ heroku local:run python3 manage.py tick --sync-airbnb
