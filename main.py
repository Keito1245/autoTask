# main.py conceptual example
from fastapi import FastAPI, BackgroundTasks
from automation.wuxia import run_wuxia_daily

app = FastAPI()

@app.post("/trigger-daily/wuxia")
async def trigger_wuxia(background_tasks: BackgroundTasks):
    # We run it as a background task so your phone gets an
    # immediate "Accepted" response rather than waiting for the script to finish.
    background_tasks.add_task(run_wuxia_daily)
    return {"status": "Accepted", "message": "Wuxia routine started."}