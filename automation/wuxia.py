from playwright.sync_api import sync_playwright
import requests


import os
from dotenv import load_dotenv

load_dotenv() 

LOCAL_PROFILE_PATH = os.getenv("LOCAL_PROFILE_PATH")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def discord_notification(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

def run_wuxia_daily():
    try:
        with sync_playwright() as p:
            # Launch using the dedicated, pre-logged-in profile
            context = p.chromium.launch_persistent_context(
                user_data_dir=LOCAL_PROFILE_PATH,
                channel="chrome",
                #Keep as False to watch it work. Change to True when you want it to run invisibly
                headless=True 
            )
            
            # Persistent contexts automatically open one blank page, so we use that one
            page = context.pages[0] if context.pages else context.new_page()
            
            print("Loading Wuxiaworld...")
            page.goto("https://www.wuxiaworld.com")
            
            
            print("Waiting for page and potential popups to load...")
            # Give the site 5 seconds to trigger any delayed daily popups
            page.wait_for_timeout(5000) 
            
            # Target the specific button text
            daily_button = page.get_by_role("button", name="Continue Reading")
            
            # Conditional logic: only click if it actually exists today
            if daily_button.is_visible():
                print("Streak popup found! Clicking 'Continue Reading'...")
                daily_button.first.click()
                
                # Optional: wait a moment to ensure the click registers before closing
                page.wait_for_timeout(5000)
                discord_notification("Successfully clicked the daily streak popup on Wuxiaworld!")
            else:
                #page.goto("https://identity.wuxiaworld.com/Account/Login")
                print("No popup today. Skipping...")
                discord_notification("No popup today, check login status if you expected one.")

                
            print("Daily automation task complete!")
            
            # Safely close the context so the profile folder is ready for the next run
            context.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        discord_notification(f"An error occurred during Wuxiaworld automation: {e}")

if __name__ == "__main__":
    run_wuxia_daily()