from pydantic import BaseModel

class UploadResponse(BaseModel):
    job_id: str
    document_id: str
    status: str
    message: str
