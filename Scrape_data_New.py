from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# List of URLs for each state's bus booking pages
state_urls = {
    "Rajasthan": "https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile",
    "Telangana": "https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile",
    "Chandigarh": "https://www.redbus.in/online-booking/chandigarh-transport-undertaking-ctu",
    "Himachal Pradesh": "https://www.redbus.in/online-booking/himachal-pradesh-tourism-development-corporation-hptdc",
    "Kerala": "https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile",
    "Jammu and Kashmir": "https://www.redbus.in/online-booking/jksrtc",
    "Assam": "https://www.redbus.in/online-booking/astc/?utm_source=rtchometile",
    "Kadamba": "https://www.redbus.in/online-booking/ktcl/?utm_source=rt",
    "West Bengal": "https://www.redbus.in/online-booking/wbtc-ctc/?utm_source=rtchometile",
}

def initialize_driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

def load_page(driver, url):
    driver.get(url)
    time.sleep(30)

def scrape_bus_routes(driver, limit=10):
    route_elements = driver.find_elements(By.CLASS_NAME, 'route')
    bus_routes_link = [route.get_attribute('href') for route in route_elements[:limit]]
    bus_routes_name = [route.text.strip() for route in route_elements[:limit]]
    return bus_routes_link, bus_routes_name

def scrape_bus_details(driver, url, route_name):
    try:
        driver.get(url)
        time.sleep(5)
        
        view_buses_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button"))
        )
        driver.execute_script("arguments[0].click();", view_buses_button)
        time.sleep(5)

        bus_name_elements = driver.find_elements(By.CLASS_NAME, "travels.lh-24.f-bold.d-color")
        bus_type_elements = driver.find_elements(By.CLASS_NAME, "bus-type.f-12.m-top-16.l-color.evBus")
        departing_time_elements = driver.find_elements(By.CLASS_NAME, "dp-time.f-19.d-color.f-bold")
        duration_elements = driver.find_elements(By.CLASS_NAME, "dur.l-color.lh-24")
        reaching_time_elements = driver.find_elements(By.CLASS_NAME, "bp-time.f-19.d-color.disp-Inline")
        star_rating_elements = driver.find_elements(By.XPATH, "//div[@class='rating-sec lh-24']")
        price_elements = driver.find_elements(By.CLASS_NAME, "fare.d-block")

        seat_availability_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'seat-left m-top-30') or contains(@class, 'seat-left m-top-16')]")

        # Assuming the current date is used for the trip
        current_date = time.strftime("%Y-%m-%d")

        bus_details = []
        for i in range(len(bus_name_elements)):
            departing_time = departing_time_elements[i].text
            reaching_time = reaching_time_elements[i].text

            bus_detail = {
                "Route_Name": route_name,
                "Route_Link": url,
                "Bus_Name": bus_name_elements[i].text,
                "Bus_Type": bus_type_elements[i].text,
                "Date": current_date,  # Storing the current date in a separate column
                "Departing_Time": departing_time,  # Time only
                "Duration": duration_elements[i].text,
                "Reaching_Time": reaching_time,  # Time only
                "Star_Rating": star_rating_elements[i].text if i < len(star_rating_elements) else '0',
                "Price": price_elements[i].text,
                "Seat_Availability": seat_availability_elements[i].text if i < len(seat_availability_elements) else '0'
            }
            bus_details.append(bus_detail)
        return bus_details
    
    except Exception as e:
        print(f"Error occurred while scraping bus details for {url}: {str(e)}")
        return []

def scrape_all_states():
    all_bus_details = []
    
    driver = initialize_driver()
    
    for state, url in state_urls.items():
        try:
            load_page(driver, url)
            
            all_bus_routes_link, all_bus_routes_name = scrape_bus_routes(driver, limit=10)
            
            for link, name in zip(all_bus_routes_link, all_bus_routes_name):
                bus_details = scrape_bus_details(driver, link, name)
                if bus_details:
                    all_bus_details.extend(bus_details)
        
        except Exception as e:
            print(f"Error occurred while scraping data for {state}: {str(e)}")

    driver.quit()
    
    df = pd.DataFrame(all_bus_details)
    df.to_csv('all_states_bus_details.csv', index=False)

# Run the scraper for all states
scrape_all_states()
