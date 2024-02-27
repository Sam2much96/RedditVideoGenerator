import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# Config
screenshotDir = "Screenshots"
screenWidth : int = 400
screenHeight : int= 800


# Import Video Script for access to class for type safety
from videoscript import VideoScript

# BUG: Breaks when Reddit loads Dark mode. Only works in Lightmode Reddit.
# BUG : Reddit Updated Reddit UI to mobile breaking divs.
# TO DO: Refactor code to use id's instead
#
# selenium.common.exceptions.TimeoutException: Message: 
# Stacktrace:
# RemoteError@chrome://remote/content/shared/RemoteError.sys.mjs:8:8
# WebDriverError@chrome://remote/content/shared/webdriver/Errors.sys.mjs:191:5
# NoSuchElementError@chrome://remote/content/shared/webdriver/Errors.sys.mjs:509:5
# dom.find/</<@chrome://remote/content/shared/DOM.sys.mjs:136:16


def getPostScreenshots(filePrefix : str, script : VideoScript):

    # initialize web driver
    driver, wait = __setupDriver(script.url)

    # create a screen shot and store the file path to videoscript file
    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait, f"t5_{0}") 
    
    # save comments screenshots using comment id
    for commentFrame in script.frames:
        commentFrame.screenShotFile = __takeScreenshot(
            filePrefix, driver, wait, f"t1_{commentFrame.commentId}")
    
    # quit selenium driver
    driver.quit()


def __takeScreenshot(filePrefix : str, driver, wait, handle="") -> str:
    # Selector Conditional
    # Docs: https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.by.html
    #
    if (handle == "Post"):
        method = By.CLASS_NAME
    else:
        method = By.ID

    print("Taking screenshots...")
    print ("Method: ",method, "/Handle:", handle) # for debug purposes only
    # BUG: EC breaks code in above bug 2
    search = wait.until(EC.presence_of_element_located((method, handle)))

    # print(search)
    driver.execute_script("window.focus();")

    fileName : str= f"{screenshotDir}/{filePrefix}-{handle}.png"
    fp = open(fileName, "wb")
    fp.write(search.screenshot_as_png)
    fp.close()
    return fileName


def __setupDriver(url: str):
    config = configparser.ConfigParser()
    config.read('config.ini')

    options = Options()
    default_profile_path = config["Firefox"]["UserProfile"]
    profile = FirefoxProfile(default_profile_path)

    options.profile = profile
    options.headless = False
    options.enable_mobile = False

    driver = webdriver.Firefox(options=options)

    # driver = webdriver.Firefox(profile)
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.get(url)

    return driver, wait
