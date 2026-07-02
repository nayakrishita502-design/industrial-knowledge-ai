from flask import Blueprint, request, jsonify

query_bp = Blueprint('queries', __name__, url_prefix='/api/queries')


@query_bp.route('/ask', methods=['POST'])
def ask_question():
    """Query documents using RAG chatbot."""
    from backend.config import Config
    from backend.services.rag_engine import RAGEngine
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    question = data.get('question', '').strip()
    k = data.get('num_sources', 4)
    
    if not question:
        return jsonify({"error": "Question cannot be empty"}), 400
    
    try:
        rag = RAGEngine(Config.GOOGLE_API_KEY, Config.CHROMA_DB_PATH)
        result = rag.query(question, k=k)
        
        if "error" in result.get("status", ""):
            return jsonify(result), 500
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@query_bp.route('/suggest', methods=['POST'])
def suggest_questions():
    """Suggest relevant questions based on document content."""
    from backend.config import Config
    from langchain_google_genai import GoogleGenerativeAI
    from backend.routes.document_routes import get_document_store
    
    try:
        doc_store = get_document_store()
        if not doc_store:
            return jsonify({
                "suggestions": [
                    "What maintenance procedures are documented?",
                    "What equipment is mentioned in the documents?",
                    "What safety hazards are identified?",
                    "What are the inspection schedules?",
                    "Who are the responsible personnel?"
                ]
            }), 200
        
        # Get sample text from documents
        sample_text = ""
        for doc in list(doc_store.values())[:3]:
            sample_text += doc["text"][:1000] + "\n"
        
        llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=Config.GOOGLE_API_KEY
        )
        
        prompt = f"""Based on this industrial document content, suggest 5 relevant 
questions a user might want to ask:

{sample_text[:2000]}

Provide 5 specific, actionable questions as a JSON array of strings."""
        
        response = llm.invoke(prompt)
        
        # Try to parse as JSON, fallback to defaults
        import json
        try:
            suggestions = json.loads(response)
        except:
            suggestions = [
                "What maintenance was performed on key equipment?",
                "What safety procedures are documented?",
                "What are the inspection findings?",
                "Which equipment has failure records?",
                "What are the compliance requirements?"
            ]
        
        return jsonify({"suggestions": suggestions}), 200
    
    except Exception as e:
        return jsonify({
            "suggestions": [
                "What maintenance procedures are documented?",
                "What equipment failures have occurred?",
                "What safety hazards are identified?"
            ]
        }), 200