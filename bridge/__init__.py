from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}
 fastapi-bridge

PY < /dev/null
 main
