from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import gspread
import datetime
from config import jobs_list, location, results_required, sheet_url, username, password
import os
from selenium.webdriver.chrome.service import Service
# from webserver import keep_alive

gc = gspread.service_account(filename='cred.json')
sh = gc.open_by_url(sheet_url)
worksheet = sh.sheet1

# keep_alive()
print("bot it alive")


while (True):

    with open("time.txt", "r", encoding="utf8") as f:
        time_d = f.read()
        if (str(time_d) == str(datetime.date.today())):
            print("going to sleep")
            sleep(400)
            continue

    for job in jobs_list:
        # print("fetching new job")
        # sleep(30)
        options = webdriver.ChromeOptions()
        # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument('--log-level=3')
        # options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        # )
        options.add_argument('--no-sandbox')
        options.add_argument("window-size=1920,1080")
        options.add_argument('--disable-dev-shm-usage')
        #  options.add_argument("--verbose")
        options.add_argument('--headless')
        # driver = webdriver.Chrome(service=Service(executable_path=os.environ.get("CHROMEDRIVER_PATH")), options=options)
        driver = webdriver.Chrome(chrome_options=options)
        # driver.maximize_window()
        driver.get("https://www.linkedin.com")

        # login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/nav/div/a[2]"))).click()

        print(driver.current_url)

        email_field_xpath = "/html/body/div/main/div[2]/div[1]/form/div[1]/input"
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, email_field_xpath)))
        email_field.send_keys(username)

        pass_field_xpath = "/html/body/div/main/div[2]/div[1]/form/div[2]/input"
        pass_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, pass_field_xpath)))
        pass_field.send_keys(password)
        email_field.send_keys(Keys.RETURN)

        sleep(3)

        jobs_url = f"https://www.linkedin.com/jobs/search/?f_TPR=r86400&geoId=102713980&keywords={job.replace(' ','%20')}&location={location}"
        sleep(5)
        driver.get(jobs_url)
        

        results_fetched = 0

        counter = 0
        page_number = 1
        flag = True
        invalid_posts = 0

        while (flag):
            sleep(5)
            list_of_jobs = driver.find_elements_by_xpath(
                "/html/body/div[6]/div[3]/div[3]/div[2]/div/section[1]/div/div/ul/li"
            )
            print(len(list_of_jobs))
            if(len(list_of_jobs)==0):
              sleep(500)
              continue
              

            if (results_fetched >= results_required):
                break

            for job_index in range(1, len(list_of_jobs) + 1):
                try:
                    sleep(1)
                    
                    if(invalid_posts>=8):
                      flag=False
                      break

                    if (counter >= len(list_of_jobs)):
                        try:
                            WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((
                                    By.XPATH,
                                    f"/html/body/div[6]/div[3]/div[3]/div[2]/div/section[1]/div/div/section/div/ul/li[{page_number+1}]/button"
                                ))).click()
                        except:
                            flag = False
                            break
                        counter = 0
                        page_number += 1

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            f"/html/body/div[6]/div[3]/div[3]/div[2]/div/section[1]/div/div/ul/li[{job_index}]/div/div/div[1]/div[2]/div[1]/a"
                        ))).click()

                    job_title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "/html/body/div[6]/div[3]/div[3]/div[2]/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/a/h2"
                        ))).get_attribute("innerText")
                    company_name = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "/html/body/div[6]/div[3]/div[3]/div[2]/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/span[1]/span[1]"
                        ))).get_attribute("innerText")
                    location = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "/html/body/div[6]/div[3]/div[3]/div[2]/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/span[1]/span[2]"
                        ))).get_attribute("innerText")
                    try:
                        mode = WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((
                                By.XPATH,
                                "/html/body/div[6]/div[3]/div[3]/div[2]/div/section[2]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/span[1]/span[3]"
                            ))).get_attribute("innerText")
                    except:
                        mode = "Na"
                    job_url = driver.current_url

                    worksheet.append_row([
                        job_title, company_name, location, mode,
                        str(datetime.date.today()), job_url
                    ])
                    print("Fetched job", results_fetched + 1)
                    counter += 1
                    results_fetched += 1
                except:
                    print("invalid post skipping")
                    invalid_posts+=1
                    continue
        print("done with", job)
        driver.close()
      

    print("done scraping")
    with open("time.txt", "w", encoding="utf8") as f:
        f.write(str(datetime.date.today()))
