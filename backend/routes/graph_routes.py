from flask import Blueprint, request, jsonify

graph_bp = Blueprint('graph', __name__, url_prefix='/api/graph')


@graph_bp.route('/build', methods=['POST'])
def build_knowledge_graph():
    """Build knowledge graph from documents."""
    from backend.services.knowledge_graph import build_graph_from_documents
    from backend.routes.document_routes import get_document_store
    
    try:
        doc_store = get_document_store()
        
        if not doc_store:
            return jsonify({
                "status": "error",
                "message": "No documents uploaded. Please upload documents first."
            }), 400
        
        # Get all document texts
        documents = [doc["text"] for doc in doc_store.values()]
        
        # Build graph
        graph = build_graph_from_documents(documents)
        graph_data = graph.export_for_visualization()
        stats = graph.get_statistics()
        
        return jsonify({
            "status": "success",
            "nodes": graph_data["nodes"],
            "edges": graph_data["edges"],
            "statistics": stats
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@graph_bp.route('/rca', methods=['POST'])
def perform_rca():
    """Perform root cause analysis."""
    from backend.config import Config
    from backend.services.rca_agent import RootCauseAnalysisAgent
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    failure_description = data.get('failure_description', '').strip()
    equipment = data.get('equipment', '').strip()
    historical_context = data.get('historical_context', '')
    quick_mode = data.get('quick_mode', False)
    
    if not failure_description:
        return jsonify({"error": "Failure description is required"}), 400
    
    if not equipment:
        return jsonify({"error": "Equipment identifier is required"}), 400
    
    try:
        agent = RootCauseAnalysisAgent(Config.GOOGLE_API_KEY)
        
        if quick_mode:
            result = agent.quick_analysis(failure_description, equipment)
        else:
            result = agent.analyze_failure(
                failure_description, 
                equipment, 
                historical_context
            )
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@graph_bp.route('/rca/questions', methods=['POST'])
def get_investigation_questions():
    """Get suggested investigation questions for RCA."""
    from backend.config import Config
    from backend.services.rca_agent import RootCauseAnalysisAgent
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    failure_description = data.get('failure_description', '').strip()
    
    if not failure_description:
        return jsonify({"error": "Failure description is required"}), 400
    
    try:
        agent = RootCauseAnalysisAgent(Config.GOOGLE_API_KEY)
        result = agent.suggest_investigation_questions(failure_description)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@graph_bp.route('/failure-patterns/<equipment_id>', methods=['GET'])
def get_failure_patterns(equipment_id):
    """Get failure patterns for specific equipment."""
    from backend.services.knowledge_graph import build_graph_from_documents
    from backend.routes.document_routes import get_document_store
    
    try:
        doc_store = get_document_store()
        
        if not doc_store:
            return jsonify({"error": "No documents uploaded"}), 400
        
        documents = [doc["text"] for doc in doc_store.values()]
        graph = build_graph_from_documents(documents)
        
        patterns = graph.find_failure_patterns(equipment_id)
        return jsonify(patterns), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500