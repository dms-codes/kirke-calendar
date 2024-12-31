from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from ics import Calendar, Event
from datetime import datetime
import pytz

# Define the local timezone (e.g., Norway)
local_tz = pytz.timezone('Europe/Oslo')

def setup_driver():
    """Set up the Selenium WebDriver with ChromeDriverManager."""
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def extract_calendar_details(driver, item, index):
    """
    Extract details from a single calendar item.

    Args:
        item (WebElement): The calendar item element.
        index (int): The index of the calendar item.
    """
    try:
        # Extract main sections
        calendar_data = item.find_element(By.CLASS_NAME, "calendar-data")
        calendar_event = item.find_element(By.CLASS_NAME, "calendar-event")

        # Extract details
        calendar_day = calendar_data.find_element(By.CLASS_NAME, "calendar-day").text
        calendar_date = calendar_data.find_element(By.CLASS_NAME, "calendar-date").text
        event_time = calendar_event.find_element(By.CLASS_NAME, "event-time").text
        calendar_label = calendar_event.find_element(By.CLASS_NAME, "calendar-label").text
        calendar_location = calendar_event.find_element(By.CLASS_NAME, "calendar-location").text

        # Handle potential link extraction
        event_info = calendar_event.find_element(By.CLASS_NAME, "event-info")
        info_text = event_info.find_element(By.CLASS_NAME, "info-text")
        link = info_text.find_element(By.TAG_NAME, "a")
        link_href = link.get_attribute("href")
        link_text = link.text.strip()

        # Navigate to the link to extract additional details
        driver.get(link_href)
        page_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-container"))
        )
        text = page_container.text

        # Return back to the first page before moving to the next item
        driver.back()  # Go back to the previous page (first page)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "calendar-item"))
        )

        return {
            "day": calendar_day,
            "date": calendar_date,
            "time": event_time,
            "label": f"{text}",
            "link": link_href,
            "location": calendar_location,
        }

    except Exception as e:
        print(f"Error extracting details for Calendar Item {index + 1}: {e}")
        return None


def save_to_ics(events, filename="calendar.ics"):
    """
    Save event data to an .ics file.

    Args:
        events (list): List of event dictionaries.
        filename (str): The name of the .ics file to save.
    """
    calendar = Calendar()

    for event_data in events:
        raw_date = event_data["date"].strip()
        raw_time = event_data["time"].replace("kl.", "").strip()

        # Add the current year if not included in the date
        if len(raw_date.split(".")) == 2:  # Check if the year is missing
            raw_date = f"{raw_date}.2025"

        # Combine date and time into a valid datetime object
        event_datetime = datetime.strptime(f"{raw_date} {raw_time}", "%d.%m.%Y %H.%M")

        # Localize the datetime to the timezone (Europe/Oslo)
        localized_event_datetime = local_tz.localize(event_datetime, is_dst=None)  # Automatically adjusts for DST

        # If you need to convert to UTC, you can use this:
        # utc_event_datetime = localized_event_datetime.astimezone(pytz.utc)

        event = Event()
        event.name = event_data["label"]
        event.begin = localized_event_datetime  # Assign the localized datetime object
        event.location = event_data["location"]
        event.description = f"""{event_data['label']} 
More info: {event_data['link']}"""
        calendar.events.add(event)

    # Write the calendar to an .ics file
    with open(filename, "w") as file:
        file.writelines(calendar.serialize_iter())
    print(f"Events successfully saved to {filename}")

    # Write the calendar to an .ics file
    with open(filename, "w") as file:
        file.writelines(calendar.serialize_iter())
    print(f"Events successfully saved to {filename}")


def main():
    """Main function to scrape calendar details."""
    url = "https://hundvag.menighet.no/Kalender"
    driver = setup_driver()
    events = []  # List to store all events

    try:
        # Open the webpage
        driver.get(url)

        # Wait for calendar items to load
        calendar_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "calendar-item"))
        )

        # Extract and display details for each calendar item
        for index in range(len(calendar_items)):
            try:
                # Re-fetch calendar items dynamically to avoid stale elements
                calendar_items = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "calendar-item"))
                )
                item = calendar_items[index]  # Dynamically fetch the current item
                event_data = extract_calendar_details(driver, item, index)
                if event_data:
                    events.append(event_data)

            except StaleElementReferenceException:
                print(f"Stale element encountered for Calendar Item {index + 1}. Retrying...")
                continue
            except Exception as e:
                print(f"Error accessing details for Calendar Item {index + 1}: {e}")

    except Exception as e:
        print(f"Error: {e}")
        print(driver.page_source)  # Debugging aid for missing elements

    finally:
        driver.quit()  # Ensure the driver is closed

    save_to_ics(events)


if __name__ == "__main__":
    main()
