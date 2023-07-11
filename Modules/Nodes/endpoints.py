import glob

import uvicorn
from fastapi import FastAPI

app = FastAPI()

ROOT_DATA_DIR = "Data"
DATA_FILE_DIRS = glob.glob(f"{ROOT_DATA_DIR}/**", recursive=True)
DATA_FILE_NAMES = [
    "XAUUSD_GMT+0_NO-DST_M1.csv",
    "US_Brent_Crude_Oil_GMT+0_NO-DST_M1.csv",
]


@app.post("/nodetasker")
async def nodepipeline():
    ...  # todo
    # Just return something for now
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app=app, host="localhost", port=8000)
