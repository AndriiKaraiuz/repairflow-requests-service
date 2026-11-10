from fastapi import FastAPI

app = FastAPI(title="RepairFlow Requests Service")


@app.get("/health")
def health():
    return {"status": "ok"}
