import glob
from typing import List, Dict

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

ROOT_DATA_DIR = "Data"
DATA_FILE_DIRS = glob.glob(f"{ROOT_DATA_DIR}/**", recursive=True)
DATA_FILE_NAMES = [
    "XAUUSD_GMT+0_NO-DST_M1.csv",
    "US_Brent_Crude_Oil_GMT+0_NO-DST_M1.csv",
]


class InputDataParams(BaseModel):
    data_file_dirs: List[str] = DATA_FILE_DIRS
    data_file_names: List[str] = DATA_FILE_NAMES
    rename_columns: Dict[str, str] = {"Open": "open", "High": "high", "Low": "low", "Close": "close"}
    scheduler: str = 'threads'
    first_or_last: str = 'first'
    n_rows: int = 1000


class TblParams(BaseModel):
    pt_sl: List[int] = [1, 1]
    min_ret: float = 0.001
    num_threads: int = 28
    vertical_barrier_num_days: int = 0
    vertical_barrier_num_hours: int = 4
    vertical_barrier_num_minutes: int = 0
    vertical_barrier_num_seconds: int = 0


class OutputDataParams(BaseModel):
    output_file_dir: str = '.'
    output_file_name: str = "example_triple_barrier_labeled_data"
    save_output: bool = True
    output_file_type: List[str] = ["csv"]


class TripleBarrierParams(BaseModel):
    input_data_params: InputDataParams
    tbl_params: TblParams
    output_data_params: OutputDataParams


@app.post("/triplebarrier")
async def triplebarrier(triple_barrier_params: TripleBarrierParams):
    from Modules.Vectorized.Pipelines.TripleBarrierMetaLabel import TBM_labeling
    TBM_labeling(
        input_data_params=triple_barrier_params.input_data_params.dict(),
        tbl_params=triple_barrier_params.tbl_params.dict(),
        output_data_params=triple_barrier_params.output_data_params.dict(),
    )

    # Just return something for now
    return {"status": "success"}


if __name__ == "__main__":
    app.run(host="localhost", port=8000)
