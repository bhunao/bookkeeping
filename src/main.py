from fastapi import FastAPI

app = FastAPI(title="BookKeeping")


@app.get("/")
def home():
    return True
