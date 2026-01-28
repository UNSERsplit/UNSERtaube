from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def test() -> str:
    return "it works"

@app.get("/ping/{id}")#nur zum testn
def ping(id: int):
    return {"id": id}