import uvicorn
from fastapi import FastAPI
from app.views import router as views_router

app = FastAPI(title="AdviNow Interview Challenge", version="1.6")

# Include the views router
app.include_router(views_router)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8013)
