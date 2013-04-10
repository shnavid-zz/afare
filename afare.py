#!/usr/bin/env python

import mechanize
import BeautifulSoup
from datetime import date, datetime
from time import sleep
import obscure

def out_to_file(out):
    with open("igot.html", "w") as fp:
        fp.write(out)

def get_fare(from_airport, to_airport, from_date, to_date):

    br = mechanize.Browser()

    br.open(obscure.FIRST_URL)

    # Fill out the search form

    br.select_form(obscure.FIRST_FORM)

    for key, value in [
        ('originAirport', from_airport),
        ('destinationAirport', to_airport),
        ('flightParams.flightDateParams.travelMonth', [str(from_date.month)]),
        ('flightParams.flightDateParams.travelDay', [str(from_date.day)]),
        ('flightParams.flightDateParams.searchTime', ['040001']),
        ('returnDate.travelMonth', [str(to_date.month)]),
        ('returnDate.travelDay', [str(to_date.day)]),
        ('returnDate.searchTime', ['040001']),
        ('adultPassengerCount', ['1']),
        ('serviceclass', ['coach']),
        ('originAlternateAirportDistance', ['0']),
        ('destinationAlternateAirportDistance', ['0']),
        ('numberOfFlightsToDisplay', ['10']),
        ('seniorPassengerCount', ['0']),
        ('youngAdultPassengerCount', ['0']),
        ('childPassengerCount', ['0']),
        ('infantPassengerCount', ['0']),
    ]:
        br.find_control(key).value = value

    br.form.new_control('text','numberOfStopsSchedule',{'value':'1'})
    sleep(5)
    br.submit()

    br.select_form(obscure.RESULTS_FORM)
    br.find_control("flightSolution1").value = ['1']
    br.find_control("flightSolution2").value = ['1']
    sleep(2)
    br.submit()

    # Continue as anonymous user (without logging in)

    br.select_form(nr=3)
    sleep(2)
    response4 = br.submit()

    # Parse the price

    out = response4.read()
    #out_to_file(out)
    bs = BeautifulSoup.BeautifulSoup(out)

    subtotal = bs.find("tbody", {"class": obscure.PRICE_CLASS})
    price = subtotal.findNext("td").findNext("td").text
    
    return price

from_airport = "SFO"
from_date = date(year=2013, month=5, day=30)
to_airport = "CLO"
to_date = date(year=2013, month=6, day=16)
csv_fname = "prices-{from}-{to}-{from_date}-{to_date}.csv".format(
    **{'from': from_airport, 'to': to_airport, 'from_date': from_date,
      'to_date': to_date})

with open(csv_fname, "a") as fp:
    while True:
        try:
            price = get_fare(from_airport=from_airport, to_airport=to_airport,
                             from_date=from_date, to_date=to_date)
        except Exception, e:
            print(e)
            sleep(60)
        else:
            now = datetime.now()
            today = date.today()
            days = (from_date - today).days
            out = "%s,%d,%d,%d,%s" % (now, now.hour, now.weekday(), days, price)
            print(out)
            fp.write(out + "\n")
            fp.flush()
            sleep(60 * 60)