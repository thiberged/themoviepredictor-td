FROM python:3.7-buster

RUN pip install argparse mysql-connector-python beautifulsoup4 requests

copy . /usr/src/themoviepredictor

CMD python /usr/src/themoviepredictor/scrapping.py movies import --api all --for 7 