if __name__ == "main":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", reload=True)
