from playwright.sync_api import sync_playwright

def run_first_test():
    # Start Playwright
    with sync_playwright() as p:
        # Launch Chromium. headless=False means you will physically see the browser open!
        browser = p.chromium.launch(headless=False)
        
        # Create a new, isolated "incognito-like" browser context
        context = browser.new_context()
        
        # Open a new tab/page in that context
        page = context.new_page()
        
        # 1. Navigate to a website
        print("Navigating to Wikipedia...")
        page.goto("https://en.wikipedia.org")
        
        # 2. Fill out a form (the search bar)
        print("Typing in the search bar...")
        page.get_by_placeholder("Search Wikipedia").first.fill("Scuba diving")
        
        # 3. Click a button (the search button)
        print("Clicking search...")
        page.get_by_role("button", name="Search").first.click()
        
        # 4. Take a screenshot to prove it worked
        print("Taking screenshot...")
        page.screenshot(path="scuba_search_result.png")
        
        # 5. Print the page title
        print(f"Success! The page title is: {page.title()}")
        
        # Close the browser when done
        browser.close()

if __name__ == "__main__":
    run_first_test()