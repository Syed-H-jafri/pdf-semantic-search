<img width="1536" height="1024" alt="Pipeline exp" src="https://github.com/user-attachments/assets/de2f3d60-0601-466b-98fc-0c930daa58c5" />


# AI-Powered PDF Semantic Search

This project extracts product data from PDF catalogs and performs intelligent search using AI-based semantic similarity.

## 🚀 Features
- Layout-aware PDF parsing using pdfplumber
- Extraction of product IDs, descriptions, and features
- Semantic search using Sentence Transformers
- Fast similarity search using FAISS
- Returns top matching products with similarity scores

## 🛠 Tech Stack
Python | pdfplumber | Sentence Transformers | FAISS | NumPy

## ⚙️ How It Works
PDF → Text Extraction → Data Structuring → Embeddings → FAISS → Query → Top Results

## 📄 Sample PDF
[Download Product Catalog PDF](https://www.jomarvalve.com/docs/lit-jv-pc.pdf)

## ▶️ Run
pip install -r requirements.txt  
1. Download the PDF from the link above  
2. Run the script:
   python main.py  
3. Enter the path to the downloaded PDF when prompted 

## 📌 Note
The original PDF file is excluded due to size limitations.

## 👤 Author
Syed H. Jafri
