import PyPDF2
import os
import openai
import numpy as np
from typing import List, Tuple, Dict
import json

class PDFProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.max_tokens_for_context = 3000  

    def process_and_store(self, doc_id: str) -> None:

        with open(f"pdfs/{doc_id}.pdf", "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            embeddings_data = {
                "pages": []
            }
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                chunks = self._split_into_chunks(text)
                
                chunk_embeddings = [self._get_embeddings(chunk[0]) for chunk in chunks]

                page_data = {
                    "page_number": page_num + 1,
                    "chunks": [{"text": chunk[0], "start": chunk[1], "embedding": emb} for chunk, emb in zip(chunks, chunk_embeddings)]
                }
                
                embeddings_data["pages"].append(page_data)
                
                print(f"Processed page {page_num + 1}")

        os.makedirs("embeddings", exist_ok=True)
        with open(f"embeddings/{doc_id}.json", "w") as f:
            json.dump(embeddings_data, f)

    def _get_embeddings(self, text: str) -> List[float]:
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def answer_question(self, doc_id: str, question: str) -> str:
        with open(f"embeddings/{doc_id}.json", "r") as f:
            embeddings_data = json.load(f)

        question_embedding = self._get_embeddings(question)

        relevant_chunks = self._get_relevant_chunks(question_embedding, embeddings_data["pages"])
        context = self._build_context_from_chunks(relevant_chunks)

        return self._generate_answer(question, context)
    
    def _get_relevant_chunks(self, question_embedding: List[float], pages: List[Dict]) -> List[Tuple[str, float]]:
        all_chunks = []
        for page in pages:
            all_chunks.extend(page["chunks"])
        
        chunk_similarity_pairs = [
            (chunk["text"], np.dot(question_embedding, chunk["embedding"]))
            for chunk in all_chunks
        ]
        
        return sorted(chunk_similarity_pairs, key=lambda x: x[1], reverse=True)

    def _build_context_from_chunks(self, relevant_chunks: List[Tuple[str, float]]) -> str:
        context = ""
        total_tokens = 0
        
        for chunk, _ in relevant_chunks:
            chunk_tokens = len(chunk.split())
            if total_tokens + chunk_tokens > self.max_tokens_for_context:
                break
            context += chunk + " "
            total_tokens += chunk_tokens
        
        return context.strip()

    def _split_into_chunks(self, text: str) -> List[Tuple[str, int]]:
        chunks = []
        for start in range(0, len(text), self.chunk_size - self.chunk_overlap):
            end = start + self.chunk_size
            chunks.append((text[start:end], start))
        return chunks

    def _generate_answer(self, question: str, context: str) -> str:
        prompt = f"""Given the following context and question, provide a concise and accurate answer. If the answer cannot be confidently determined from the context, respond with "Data Not Available".

                Context:
                {context}

                Question: {question}

                Answer:"""

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            temperature=0.5,
        )

        return response.choices[0].message.content.strip()