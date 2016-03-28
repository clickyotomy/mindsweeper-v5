# Mindsweeper v5.0, Utsav 2016.

Mindsweeper is the official treasure hunt for Utsav.
An online treasure hunt is a game of wits and intellect
Mindsweeper is now 5 years old.

The web-application is built using Flask and it's extensions; back-end of the application (storing user and level data) is implemented using redis. As of now, the application is hosted on a free-tier instance of Google Compute Engine. For handling concurrency, the application runs on top of gunicorn to handle concurrency.
