#!/usr/bin/python
from bs4 import BeautifulSoup
import datetime
import requests
import sys
import re
import json

class TideScraper():
    def __init__(self):
        self.tide_locations = [
            {
                'city': 'Half Moon Bay, California',
                'tide_url': 'https://www.tide-forecast.com/locations/Half-Moon-Bay-California/tides/latest',
                'sun_url': 'https://www.timeanddate.com/sun/@5354943'
            },
            {
                'city': 'Huntington Beach, California',
                'tide_url': 'https://www.tide-forecast.com/locations/Huntington-Beach/tides/latest',
                'sun_url': 'https://www.timeanddate.com/sun/usa/huntington-beach'
            },
            {
                'city': 'Providence, Rhode Island',
                'tide_url': 'https://www.tide-forecast.com/locations/Providence-Rhode-Island/tides/latest',
                'sun_url': 'https://www.timeanddate.com/sun/usa/providence'
            },
            {
                'city': 'Wrightsville Beach, North Carolina',
                'tide_url': 'https://www.tide-forecast.com/locations/Wrightsville-Beach-North-Carolina/tides/latest',
                'sun_url': 'https://www.timeanddate.com/sun/@4500092'
            }
        ]


    def get_output_dictionary(self):
        self.dictionary = {}
        for location in self.tide_locations:
            self.dictionary[location['city']] = []


    @staticmethod
    def make_request(url):
        """
        Make request call to scrape website info
        :return: html formatted information
        """

        # make request
        try:
            

            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print('Unable to scrape url {0} due to: {1}.'.format(url, e))
            return None

        if response.ok:
            return response.text
        else:
            print(response.status_code)
            return None




    def get_location_tide_data(self):
        """
        We want low tides that occur after sunrise and before
        sunset. Return the time and height for each daylight low tide.
        :return: list of tide pools that meet criteria
        """

        self.get_output_dictionary()
        for location in self.tide_locations:
            times = ['', '', '', '']  # 0: first low tide | 1: second low tide | 2: sunrise | 3: sunset
            heights = ['', '']  # 0: goes with first low tide | 1: goes with second low tide
            today = datetime.datetime.today()  # grab today to add hh:mm to for comparison
            tide_counter = 0  # used to tell if a beach has a low tide in daylight hours

            # get html data for tide and sunrise/sunset by location
            tide_data = self.make_request(location['tide_url'])
            sun_data = self.make_request(location['sun_url'])

            # error handling
            if tide_data is None or sun_data is None:
                print('For location {0} failed to retrieve tide or sun data. Cannot calculate.'.format(location['city']))
                continue

            # process tide data
            try:
                tide_soup = BeautifulSoup(tide_data, 'html.parser')
            except:
                print('Beautiful soup failed to process tide data for city: {0}'.format(location['city']))
                continue

            # pull tide times and heights out of tide table and store in times and heights lists respectively
            tide_table = tide_soup.find("table", {"class": "tide-day-tides"})
            for table_row in tide_table.find_all('tr'):
                if table_row.find('td', text='Low Tide'):
                    options = table_row.find_all('b')
                    time = re.findall(r'<b>(.*)</b>', str(options[0]))
                    height = re.findall(r'primary">(.*)</b>', str(options[1]))
                    if not times[0]:
                        times[0] = time[0].strip()
                        heights[0] = height[0].strip()
                    else:
                        times[1] = time[0].strip()
                        heights[1] = height[0].strip()

            # process sunrise/sunset data
            try:
                sun_soup = BeautifulSoup(sun_data, 'html.parser')
            except:
                print('Beautiful soup failed to process sun data for city: {0}'.format(location['city']))
                continue

            # pull sun times out of table and store in times list
            sun_table = sun_soup.find("table", {"class": "table--inner-borders-rows"})
            for table_row in sun_table.find_all('tr'):
                if table_row.find('th', text='Sunrise Today: '):
                    options = table_row.find_all('td')
                    sunrise = re.findall(r'<td>(.*)<span', str(options[0]))
                    times[2] = sunrise[0].strip()
                elif table_row.find('th', text='Sunset Today: '):
                    options = table_row.find_all('td')
                    sunset = re.findall(r'<td>(.*)<span', str(options[0]))
                    times[3] = sunset[0].strip()

            # make times in 24 hour clock for easier comparison
            for x in range(len(times)):
                time_m_list = times[x].split(' ')
                time_list = time_m_list[0].split(':')
                hour = time_list[0]
                minute = time_list[1]
                meridiem = time_m_list[1]

                # check meridiem; if pm add 12 hours
                if re.search(r'pm', meridiem, re.IGNORECASE):
                    hour = int(hour) + 12

                # convert to datetime format to compare
                time = '{0}:{1}'.format(hour, minute)
                dt_time = datetime.datetime.combine(today, datetime.datetime.strptime(time, '%H:%M').time())
                times[x] = dt_time

            # determine if tides fall during sunlight hours
            if times[3] > times[0] > times[2]:
                print('Go to {0} at {1}. Found low tide with height {2} during daylight hours'.format(location['city'],
                                                                                                      times[0],
                                                                                                      heights[0]))
                self.dictionary[location['city']].append({f'{times[0]}': heights[0]})
                tide_counter += 1
            if times[3] > times[1] > times[2]:
                print('Go to {0} at {1}. Found low tide with height {2} during daylight hours'.format(location['city'],
                                                                                                      times[1],
                                                                                                      heights[1]))
                self.dictionary[location['city']].append({f'{times[1]}': heights[1]})
                tide_counter += 1
            if tide_counter == 0:
                print('Don\'t go to {0} today. Did not find a low tide within daylight hours'.format(location['city']))

    def write_output(self):
        with open('output.json', 'w') as f:
            json.dump(self.dictionary, f, indent=2)



if __name__ == "__main__":

    scraper = TideScraper()
    scraper.get_location_tide_data()
    scraper.write_output()
    sys.exit(0)
