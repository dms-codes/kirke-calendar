# Calendar Scraper

This project scrapes event details from a calendar on a specific website and saves them to an `.ics` (iCalendar) file. It uses Selenium for web scraping and `ics.py` for creating and exporting the calendar data.

## Features

- Scrapes calendar data (event date, time, location, description, and more) from a website.
- Extracts additional event details from individual event pages.
- Saves the event data to an `.ics` file, which can be imported into most calendar applications.
  
## Prerequisites

Before running the script, ensure that you have the following installed:

- Python 3.x
- pip (Python package manager)

## Installation

1. Clone this repository to your local machine or download the script file.
2. Install the required Python packages by running:

```bash
pip install -r requirements.txt
