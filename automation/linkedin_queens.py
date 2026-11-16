import re
import requests
import math
from playwright.sync_api import sync_playwright
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
def scrape_queens_board(page):

    print("starting game...")
    page.goto("https://www.linkedin.com/games/queens/?skipStartScreen=true")
    page.wait_for_selector("div[data-testid='interactive-grid']")

    cell_elements = page.locator("div[data-cell-idx]").all()
    total_cells = len(cell_elements)
    grid_size = math.isqrt(total_cells)

    print(f"Total cells: {total_cells}, Grid size: {grid_size}x{grid_size}")

    color_to_id={}
    next_id = 0
    board = []
    current_row = []

    for cell in cell_elements:
        label = cell.get_attribute("aria-label")
        match = re.search(r"color (.*?), row", label)
        if match:
            color_name = match.group(1)
            if color_name not in color_to_id:
                color_to_id[color_name] = next_id
                next_id += 1

            current_row.append(color_to_id[color_name])

            if len(current_row) == grid_size:
                board.append(current_row)
                current_row = []

    print("scraped board:")
    for row in board:
        print(row)

    print("\nColor key:", color_to_id)
    return board, grid_size


def solve_queens(board):
    grid_size = len(board)
    cols_used = set()
    regions_used = set()
    placed_queens = []

    def is_safe(r,c,color_id):
        if c in cols_used:
            return False
        if color_id in regions_used:
            return False
        for qr, qc in placed_queens:
            if abs(r-qr) <= 1 and abs(c-qc) <= 1:
                return False
        return True

    def backtrack(row):
        if row == grid_size:
            return True
        for col in range(grid_size):
            color_id = board[row][col]
            if is_safe(row, col, color_id):
                placed_queens.append((row, col))
                cols_used.add(col)
                regions_used.add(color_id)

                if backtrack(row + 1):
                    return True

                placed_queens.pop()
                cols_used.remove(col)
                regions_used.remove(color_id)
        return False
    print("\nSolving puzzle...")
    success = backtrack(0)

    if success:
        print(f"Solved! Winning coordinates: {placed_queens}")
        return placed_queens
    else:
        print("Failed to find a solution. Check board parsing.")
        return []
    
def place_crowns(page, winning_cords, grid_size):
    print("Placing crowns on the board...")
    for row, col in winning_cords:
        cell_idx = (row*grid_size)+col
        cell = page.locator(f"div[data-cell-idx='{cell_idx}']")
        cell.click()
        page.wait_for_timeout(500)  # Small delay to ensure the click registers
        cell.click()  
        page.wait_for_timeout(500)  # Small delay to ensure the click registers
    print("done")
    page.wait_for_timeout(2000)  # Wait a bit before closing the context


def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=LOCAL_PROFILE_PATH,
            channel="chrome",
            headless=True)

        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.linkedin.com/games/queens/?skipStartScreen=true")
        board, grid_size = scrape_queens_board(page)
        winning_cords= solve_queens(board)  
        if winning_cords:
            place_crowns(page, winning_cords, grid_size)
            discord_notification("Successfully solved the LinkedIn Queens puzzle and placed crowns!")
        else:
            discord_notification("Failed to solve the LinkedIn Queens puzzle.")
        context.close()
if __name__ == "__main__":
    main()  