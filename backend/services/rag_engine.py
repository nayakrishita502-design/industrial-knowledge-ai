import os
from typing import Dict, List, Optional
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class RAGEngine:
    """RAG engine using LangChain with Gemini."""
    
    INDUSTRIAL_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are an expert industrial equipment analyst with deep knowledge of 
maintenance procedures, safety protocols, and equipment operations.

Answer the following question based ONLY on the provided industrial documents. 
Be specific and include:
- Equipment references (model numbers, IDs)
- Dates and timelines
- Procedure numbers (SOPs, work orders)
- Safety considerations and hazards
- Personnel involved

Context from documents:
{context}

Question: {question}

Provide a detailed, accurate answer with specific references. If the information
is not available in the provided documents, clearly state: "This information is
not available in the provided documents."

Answer:"""
    )
    
    def __init__(self, google_api_key: str, chroma_path: str = "./data/chromadb"):
        """Initialize RAG engine."""
        if not google_api_key:
            raise ValueError("Google API key is required")
        
        os.environ["GOOGLE_API_KEY"] = google_api_key
        
        # Initialize LLM
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=google_api_key
        )
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_api_key
        )
        
        # ChromaDB path
        self.chroma_path = chroma_path
        os.makedirs(chroma_path, exist_ok=True)
        
        # Initialize vectorstore
        self.vectorstore = None
        self._initialize_vectorstore()
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _initialize_vectorstore(self):
        """Initialize or load vectorstore."""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings,
                collection_name="industrial_docs"
            )
        except Exception as e:
            print(f"Error initializing vectorstore: {e}")
            self.vectorstore = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings,
                collection_name="industrial_docs"
            )
    
    def ingest_documents(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict]] = None
    ) -> Dict:
        """Ingest documents into vectorstore."""
        try:
            # Split texts into chunks
            all_chunks = []
            all_metadatas = []
            
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                all_chunks.extend(chunks)
                
                # Assign metadata to each chunk
                if metadatas and i < len(metadatas):
                    all_metadatas.extend([metadatas[i]] * len(chunks))
            
            if not all_chunks:
                return {"status": "error", "message": "No valid chunks to ingest"}
            
            # Add to vectorstore
            if all_metadatas and len(all_metadatas) == len(all_chunks):
                self.vectorstore.add_texts(texts=all_chunks, metadatas=all_metadatas)
            else:
                self.vectorstore.add_texts(texts=all_chunks)
            
            # Persist changes
            self.vectorstore.persist()
            
            return {
                "status": "success",
                "chunks_added": len(all_chunks),
                "documents_processed": len(texts)
            }
        
        except Exception as e:
            print(f"Error ingesting documents: {e}")
            return {"status": "error", "message": str(e)}
    
    def query(self, question: str, k: int = 4) -> Dict:
        """Query documents using RAG."""
        if not question.strip():
            return {"status": "error", "message": "Question cannot be empty"}
        
        try:
            # Create retriever
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            
            # Get relevant documents
            docs = retriever.get_relevant_documents(question)
            
            if not docs:
                return {
                    "answer": "No relevant documents found. Please upload documents first.",
                    "sources": [],
                    "num_sources": 0
                }
            
            # Build context from retrieved docs
            context = "\n\n---\n\n".join([doc.page_content for doc in docs])
            
            # Generate response
            prompt = self.INDUSTRIAL_PROMPT.format(
                context=context,
                question=question
            )
            
            response = self.llm.invoke(prompt)
            
            # Extract sources
            sources = []
            for doc in docs:
                source_text = doc.page_content[:300]
                if len(doc.page_content) > 300:
                    source_text += "..."
                sources.append({
                    "content": source_text,
                    "metadata": doc.metadata if doc.metadata else {}
                })
            
            return {
                "answer": response,
                "sources": sources,
                "num_sources": len(docs)
            }
        
        except Exception as e:
            print(f"Error querying: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vectorstore."""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "document_count": count,
                "collection_name": "industrial_docs"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear_collection(self) -> Dict:
        """Clear all documents from the vectorstore."""
        try:
            self.vectorstore.delete_collection()
            self._initialize_vectorstore()
            return {"status": "success", "message": "Collection cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}