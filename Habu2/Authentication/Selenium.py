import platform
import time
from rich import print
from seleniumwire import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common import by
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import re
import json


# https://github.com/dirkjanm/ROADtools/blob/f63fa32392cfc78c1c2615b977d3e8a317dd90ca/roadtx/roadtools/roadtx/selenium.py#L157

def GetRefreshToken(driver):
    driver.get("https://intune.microsoft.com/#home")
    time.sleep(15)
    
    tokens = tokens = {"portal_refresh_token": None}

    for k, v in driver.execute_script("return window.sessionStorage").items():
        if re.match(".*refreshtoken.*", k):
            cookie = json.loads(v)
            tokens["portal_refresh_token"] = cookie["secret"]
    
    if tokens["portal_refresh_token"] == None:
        tokens = "Intune portal refresh token could not be acquired!"
        
    return tokens

def GetTokens(driver):
    driver.get("https://security.microsoft.com/v2/advanced-hunting")
    time.sleep(15)

    tokens = {"sccauth": driver.get_cookie("sccauth")["value"]}

    for request in driver.requests:
        if request.url == "https://security.microsoft.com/api/auth/IsInRoles?cache=true":
            tokens.update({"x-xsrf-token": request.headers.get("x-xsrf-token")})
    
    if tokens["sccauth"] == None or "x-xsrf-token" not in tokens:
        tokens = "Could not obtain necessary tokens!"
    
    return tokens
            
def main(username, password, portal):
    portals = {
        "security": "https://security.microsoft.com/",
        "intune": "https://intune.microsoft.com/"
    }

    portalUrl = portals[portal]
    driver = None

    print(f"[bold cyan]Logging in as {username}...[/bold cyan]")
    if platform.system() == "Windows":
        options = webdriver.EdgeOptions()
        options.add_argument("headless")
        options.add_argument("disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Edge(options=options)
    elif platform.system() == "Darwin":
        options = webdriver.SafariOptions()
        driver = webdriver.Safari()
    elif platform.system() == "Linux":
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

    
    driver.get(portalUrl)
    WebDriverWait(driver, timeout=15, poll_frequency=.2).until(ec.any_of(ec.presence_of_element_located((by.By.ID, "i0116"))))
    ms_user_input = driver.find_element(by.By.ID, "i0116")
    ms_user_input.clear()
    ms_user_input.click()
    ms_user_input.send_keys(username)
    ms_user_input.send_keys(Keys.ENTER)

    time.sleep(2)

    password_input = WebDriverWait(driver, timeout=15, ).until(
        ec.any_of(
            ec.presence_of_element_located((by.By.ID, "i0118")),
            ec.presence_of_element_located((by.By.ID, "Password"))    
    ))

    if password_input:
        password_input.clear()
        password_input.click()
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

    final_btn = WebDriverWait(driver, timeout=10).until(ec.presence_of_element_located((by.By.ID, "idSIButton9")))
    final_btn.click()

    # print(f"[bold cyan]Logged in...[/bold cyan]")
    # print(f"[bold cyan]Gathering cookies and headers...[/bold cyan]")

    # portalUrl = portals[portal]
    response = None

    match portal:
        case "security":
            response = GetTokens(driver)
        case "intune":
            response = GetRefreshToken(driver)

    # print(f"[bold cyan]Done![/bold cyan]")
    driver.close()

    return response