from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
from uuid import uuid4
from pdf_processor import PDFProcessor
from slack_utils import SlackUtils

app = FastAPI(title="PDF Question Answering Agent",debug=True)

class Question(BaseModel):
    text: str

class AnswerRequest(BaseModel):
    doc_id: str
    questions: List[Question]

pdf_processor = PDFProcessor()
slack_utils = SlackUtils()

@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    if file.filename.split(".")[-1].lower() != "pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    doc_id = str(uuid4())
    content = file.file.read()  
    
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{doc_id}.pdf"
    with open(file_path, "wb") as pdf_file:
        pdf_file.write(content)
    
    pdf_processor.process_and_store(doc_id)
    
    
    return {"message": "PDF uploaded, processed, and embeddings stored successfully", "doc_id": doc_id}

@app.post("/answer-questions")
async def answer_questions(request: AnswerRequest):
    if not os.path.exists(f"pdfs/{request.doc_id}.pdf"):
        raise HTTPException(status_code=404, detail="PDF not found. Please upload the PDF first.")

    if not os.path.exists(f"embeddings/{request.doc_id}.json"):
        raise HTTPException(status_code=404, detail="Embeddings not found. Please reupload the PDF.")

    answers = []
    for question in request.questions:
        answer = pdf_processor.answer_question(request.doc_id, question.text)
        answers.append({
            "question": question.text,
            "answer": answer
        })


    slack_message = "Question Answering Results:\n\n"
    for qa in answers:
        slack_message += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
    slack_utils.post_message(slack_message)

    return answers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000,log_level="debug")