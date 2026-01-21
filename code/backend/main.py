from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def test() -> str:
    return "it works"