"""
Screenshot.py

Features:
(1) Takes screenshots of the reddit post title and comments
(2) Uses The comment's and titles div id + selenium to take the screenshots

Bugs:
(1) Doesn't screenshot post boarders and dp, only the comments and text
"""
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




def getPostScreenshots(filePrefix : str, script : VideoScript) -> None:
    #print("file name: ",filePrefix)
    print("file id: ", script.fileId)

    # initialize web driver
    driver, wait = __setupDriver(script.url)

    # create a screen shot and store the file path to videoscript file
    # formatted string is addapted to Reddit's New UI divs
    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait, f"post-title-t3_{script.fileId}") 
    
    # save comments screenshots using comment id
    for commentFrame in script.frames:
        commentFrame.screenShotFile = __takeScreenshot(
            filePrefix, driver, wait, f"t1_{commentFrame.commentId}-comment-rtjson-content")
    
    # quit selenium driver
    driver.quit()


def __takeScreenshot(filePrefix : str, driver, wait, handle="") -> str:
    # Selector Conditional
    # Docs: https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.by.html
    #
    print("Handle debug: ", handle)
    if (handle == "post"):
        method = By.CLASS_NAME
    else:
        method = By.ID

    print("Taking screenshots...")
    print ("Method: ",method, "/Handle:", handle) # for debug purposes only
    # BUG: EC breaks code in above bug 2
    try:
        search = wait.until(EC.presence_of_element_located((method, handle)))
        # print(search)
        driver.execute_script("window.focus();")

        fileName : str= f"{screenshotDir}/{filePrefix}-{handle}.png"
        fp = open(fileName, "wb")
        fp.write(search.screenshot_as_png)
        fp.close()
        return fileName
    except :
        print(f"Error: Selenium.common.exceptions.TImeoutExceptions timeout error")


    
    


def __setupDriver(url: str):
    config = configparser.ConfigParser()
    config.read('config.ini')

    options = Options()
    default_profile_path = config["Firefox"]["UserProfile"]
    profile = FirefoxProfile(default_profile_path)

    options.profile = profile
    options.headless = False
    options.enable_mobile = False
    options.set_preference("dom.webdriver.enabled", False)  # helps bypass bot detection
    options.set_preference("useAutomationExtension", False)



    driver = webdriver.Firefox(options=options)
    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.set_page_load_timeout(80)  # 80s max wait
    try: 
        driver.get(url)
    except Exception as e:
        print(f"[WARN] Page load failed or timed out: {e}")
        # try a lighter load (stop loading scripts/images if needed)
        driver.execute_script("window.stop();")
    
    wait = WebDriverWait(driver, 10)

    return driver, wait
