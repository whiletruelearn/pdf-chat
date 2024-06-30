# PDF Question Answering Agent

This project implements a FastAPI-based web service that allows users to upload PDF documents, ask questions about the content, and receive answers posted to Slack. 

## Features

- PDF upload and processing
- Question answering based on PDF content
- Posting results to Slack
- FastAPI web service with Swagger UI

## Requirements

- Python 3.8+
- FastAPI
- OpenAI API
- PyPDF2
- Slack SDK

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/whiletruelearn/pdf-chat.git
   cd pdf-chat
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export SLACK_HOOK=your_slack_webhook_key
   ```

## Usage

1. Start the FastAPI server:
   ```
   python src/main.py
   ```

2. Open your browser and navigate to `http://localhost:8000/docs` to access the Swagger UI.

3. Use the `/upload-pdf` endpoint to upload a PDF file.

4. Use the `/answer-questions` endpoint to submit questions and get answers based on the uploaded PDF content.


## API Endpoints

- `POST /upload-pdf`: Upload a PDF file for processing. Gives a document id
- `POST /answer-questions`: Submit questions and get answers based on the PDF content.

