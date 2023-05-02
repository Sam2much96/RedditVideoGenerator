import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# Config
screenshotDir = "Screenshots"
screenWidth = 400
screenHeight = 800


# BUG: Breaks when Reddit loads Dark mode. Only works in Lightmode Reddit.

def getPostScreenshots(filePrefix, script):
    print("Taking screenshots...")
    driver, wait = __setupDriver(script.url)
    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait)
    for commentFrame in script.frames:
        commentFrame.screenShotFile = __takeScreenshot(
            filePrefix, driver, wait, f"t1_{commentFrame.commentId}")
    driver.quit()


def __takeScreenshot(filePrefix, driver, wait, handle="Post"):
    if (handle == "Post"):
        method = By.CLASS_NAME
    else:
        method = By.ID

    # print (method) # for debug purposes only

    search = wait.until(EC.presence_of_element_located((method, handle)))

    # print(search)
    driver.execute_script("window.focus();")

    fileName = f"{screenshotDir}/{filePrefix}-{handle}.png"
    fp = open(fileName, "wb")
    fp.write(search.screenshot_as_png)
    fp.close()
    return fileName


def __setupDriver(url: str):
    config = configparser.ConfigParser()
    config.read('config.ini')

    options = Options()  # webdriver.FirefoxOptions()
    # default_profile_path = '/home/samuel/snap/firefox/common/.mozilla/firefox/7yg3hm8t.RedditVidGen'
    default_profile_path = config["Firefox"]["UserProfile"]
    profile = FirefoxProfile(default_profile_path)
    # profile.set_preference("javascript.enabled", False)

    options.profile = profile
    options.headless = False
    options.enable_mobile = False

    # profile = '/home/samuel/.mozilla/firefox/profiles.ini'
    driver = webdriver.Firefox(options=options)

    # driver = webdriver.Firefox(profile)
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.get(url)

    return driver, wait
