from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
import uvicorn
from document_detector import detect_document_border

app = FastAPI(title="Document Border Detection API")

@app.post("/detect-border/")
async def detect_border(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        processed_image_bytes = detect_document_border(contents)
        
        return Response(content=processed_image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
