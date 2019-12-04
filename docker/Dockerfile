FROM python:3.7-buster

RUN pip install argparse requests mysql-connector-python beautifulsoup4 isodate

COPY . /usr/src/themoviepredictor

WORKDIR /usr/src/themoviepredictor

# CMD python /usr/src/themoviepredictor/scrapping.py movies import --api all --for 7 