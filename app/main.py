from fastapi import FastAPI

app = FastAPI(title="DEX Sniping Platform")

@app.get("/")
def root():
    return {"message": "DEX Sniping Platform is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
