# Tides Scraper

A Python script for scraping daylight low-tides from https://www.tide-forecast.com/ 

#Installation steps

1. git clone https://github.com/Anila18/tides-scraper.git
Setup:

```
cd tides-scraper
pip install -r requirements.txt 

```

#Running Script

```
python scraper.py
```
#Output

The output is returned to file output.json

# The Approach

The process by which this data is scraped in a nutshell entails requesting the page for the given location, locating the tide table within it, and sequentially reading the rows of the table, managing the daytime state and recording low-tides for the final output