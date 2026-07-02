from flask import Blueprint, request, jsonify

compliance_bp = Blueprint('compliance', __name__, url_prefix='/api/compliance')


@compliance_bp.route('/check', methods=['POST'])
def check_compliance():
    """Check document against compliance standards."""
    from backend.services.compliance_checker import ComplianceChecker
    from backend.routes.document_routes import get_document_store
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    document_text = data.get('document_text', '')
    standards = data.get('standards', ['Factory_Act', 'ISO_45001'])
    filename = data.get('filename', 'uploaded_document')
    
    # If no document text provided, try to use stored documents
    if not document_text:
        doc_store = get_document_store()
        if doc_store:
            # Combine all document texts
            document_text = "\n\n".join([doc["text"] for doc in doc_store.values()])
        else:
            return jsonify({
                "error": "No document text provided and no documents uploaded"
            }), 400
    
    try:
        checker = ComplianceChecker()
        check_result = checker.check_document(document_text, standards)
        report = checker.generate_report(check_result, filename)
        
        return jsonify({
            "status": "success",
            "compliance_score": check_result["compliance_score"],
            "summary": report["summary"],
            "findings": check_result["findings"],
            "action_items": report["action_items"],
            "standards_checked": standards
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@compliance_bp.route('/standards', methods=['GET'])
def get_standards():
    """Get available compliance standards."""
    from backend.services.compliance_checker import ComplianceChecker
    
    checker = ComplianceChecker()
    standards = checker.get_available_standards()
    
    return jsonify({
        "standards": standards
    }), 200


@compliance_bp.route('/report', methods=['POST'])
def generate_report():
    """Generate a compliance report."""
    from backend.services.compliance_checker import ComplianceChecker
    from backend.routes.document_routes import get_document_store
    
    data = request.json
    standards = data.get('standards', ['Factory_Act', 'OISD', 'ISO_45001'])
    
    doc_store = get_document_store()
    if not doc_store:
        return jsonify({"error": "No documents uploaded"}), 400
    
    try:
        document_text = "\n\n".join([doc["text"] for doc in doc_store.values()])
        
        checker = ComplianceChecker()
        check_result = checker.check_document(document_text, standards)
        report = checker.generate_report(check_result, "combined_documents")
        
        return jsonify({
            "status": "success",
            "report": report
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500