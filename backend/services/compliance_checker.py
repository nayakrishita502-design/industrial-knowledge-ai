import re
from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class ComplianceRule:
    """Represents a compliance rule."""
    id: str
    standard: str
    requirement: str
    keywords: List[str]
    priority: str = "MEDIUM"


class ComplianceChecker:
    """Check documents against industrial compliance standards."""
    
    COMPLIANCE_RULES = {
        "Factory_Act": [
            ComplianceRule(
                "FA001", "Factory_Act", 
                "Safety officer designation",
                ["safety officer", "designated safety", "safety personnel", "safety supervisor"],
                "HIGH"
            ),
            ComplianceRule(
                "FA002", "Factory_Act",
                "Regular inspection schedules documented",
                ["inspection schedule", "regular inspection", "periodic inspection", "inspection frequency"],
                "HIGH"
            ),
            ComplianceRule(
                "FA003", "Factory_Act",
                "PPE requirements specified",
                ["ppe", "personal protective equipment", "safety gear", "protective equipment", "helmet", "gloves", "goggles"],
                "HIGH"
            ),
            ComplianceRule(
                "FA004", "Factory_Act",
                "Emergency procedures documented",
                ["emergency procedure", "emergency response", "emergency evacuation", "fire drill", "emergency exit"],
                "HIGH"
            ),
            ComplianceRule(
                "FA005", "Factory_Act",
                "Worker training records",
                ["training record", "worker training", "safety training", "competency assessment", "certification"],
                "MEDIUM"
            ),
            ComplianceRule(
                "FA006", "Factory_Act",
                "Incident reporting procedures",
                ["incident report", "accident report", "near miss", "incident investigation", "root cause"],
                "MEDIUM"
            ),
            ComplianceRule(
                "FA007", "Factory_Act",
                "Working hours and overtime documentation",
                ["working hours", "overtime", "shift schedule", "rest period", "break time"],
                "LOW"
            ),
        ],
        "OISD": [
            ComplianceRule(
                "OISD001", "OISD",
                "Pressure vessel certifications",
                ["pressure vessel", "vessel certification", "pressure test", "hydrostatic test", "vessel inspection"],
                "HIGH"
            ),
            ComplianceRule(
                "OISD002", "OISD",
                "Pipeline specifications documented",
                ["pipeline spec", "piping specification", "pipeline design", "pipe schedule", "material specification"],
                "HIGH"
            ),
            ComplianceRule(
                "OISD003", "OISD",
                "Valve maintenance schedules",
                ["valve maintenance", "valve inspection", "valve test", "safety valve", "relief valve"],
                "MEDIUM"
            ),
            ComplianceRule(
                "OISD004", "OISD",
                "Gas detection systems documented",
                ["gas detection", "gas monitor", "combustible gas", "toxic gas", "gas alarm"],
                "HIGH"
            ),
            ComplianceRule(
                "OISD005", "OISD",
                "Emergency shutdown procedures",
                ["emergency shutdown", "esd", "trip system", "shutdown procedure", "process shutdown"],
                "HIGH"
            ),
            ComplianceRule(
                "OISD006", "OISD",
                "Hot work permit procedures",
                ["hot work", "welding permit", "fire watch", "hot work permit", "flame work"],
                "MEDIUM"
            ),
            ComplianceRule(
                "OISD007", "OISD",
                "Fire fighting equipment documentation",
                ["fire extinguisher", "fire fighting", "fire suppression", "fire hydrant", "foam system"],
                "MEDIUM"
            ),
        ],
        "ISO_45001": [
            ComplianceRule(
                "ISO001", "ISO_45001",
                "Hazard identification process",
                ["hazard identification", "hazid", "hazard assessment", "hazard register", "hazard analysis"],
                "HIGH"
            ),
            ComplianceRule(
                "ISO002", "ISO_45001",
                "Risk assessment procedures",
                ["risk assessment", "risk analysis", "risk matrix", "risk evaluation", "risk register"],
                "HIGH"
            ),
            ComplianceRule(
                "ISO003", "ISO_45001",
                "Control measures documented",
                ["control measure", "risk control", "mitigation", "safeguard", "protective measure"],
                "HIGH"
            ),
            ComplianceRule(
                "ISO004", "ISO_45001",
                "Incident investigation procedures",
                ["incident investigation", "accident investigation", "root cause analysis", "rca", "corrective action"],
                "MEDIUM"
            ),
            ComplianceRule(
                "ISO005", "ISO_45001",
                "Competence and training requirements",
                ["competence", "training requirement", "skill assessment", "qualification", "training needs"],
                "MEDIUM"
            ),
            ComplianceRule(
                "ISO006", "ISO_45001",
                "Management review documentation",
                ["management review", "review meeting", "performance review", "audit finding", "improvement plan"],
                "LOW"
            ),
            ComplianceRule(
                "ISO007", "ISO_45001",
                "Worker participation and consultation",
                ["worker participation", "consultation", "safety committee", "worker representative", "feedback"],
                "LOW"
            ),
        ]
    }
    
    def __init__(self):
        self.findings = []
    
    def check_document(self, document_text: str, standards: List[str]) -> Dict:
        """Check document against specified standards."""
        doc_lower = document_text.lower()
        
        findings = {
            "compliant": [],
            "non_compliant": [],
            "partial": [],
            "by_standard": {},
            "by_priority": {"HIGH": [], "MEDIUM": [], "LOW": []}
        }
        
        total_rules = 0
        compliant_count = 0
        
        for standard in standards:
            if standard not in self.COMPLIANCE_RULES:
                continue
            
            standard_findings = {"compliant": [], "non_compliant": [], "partial": []}
            
            for rule in self.COMPLIANCE_RULES[standard]:
                total_rules += 1
                
                # Check how many keywords match
                matches = sum(1 for kw in rule.keywords if kw in doc_lower)
                match_ratio = matches / len(rule.keywords)
                
                result = {
                    "rule_id": rule.id,
                    "standard": rule.standard,
                    "requirement": rule.requirement,
                    "priority": rule.priority,
                    "keywords_found": matches,
                    "keywords_total": len(rule.keywords),
                    "match_ratio": round(match_ratio, 2)
                }
                
                if match_ratio >= 0.5:
                    findings["compliant"].append(result)
                    standard_findings["compliant"].append(result)
                    compliant_count += 1
                elif match_ratio > 0:
                    findings["partial"].append(result)
                    standard_findings["partial"].append(result)
                    compliant_count += 0.5
                else:
                    findings["non_compliant"].append(result)
                    standard_findings["non_compliant"].append(result)
                
                # Add to priority grouping
                findings["by_priority"][rule.priority].append(result)
            
            findings["by_standard"][standard] = standard_findings
        
        # Calculate compliance score
        compliance_score = round((compliant_count / total_rules) * 100, 1) if total_rules > 0 else 0
        
        return {
            "compliance_score": compliance_score,
            "total_rules_checked": total_rules,
            "compliant_count": len(findings["compliant"]),
            "partial_count": len(findings["partial"]),
            "non_compliant_count": len(findings["non_compliant"]),
            "findings": findings
        }
    
    def generate_report(self, check_result: Dict, filename: str) -> Dict:
        """Generate a compliance report."""
        findings = check_result["findings"]
        
        # Generate action items (prioritize by priority level)
        action_items = []
        
        # High priority non-compliant items first
        for item in findings["non_compliant"]:
            if item["priority"] == "HIGH":
                action_items.append({
                    "priority": "CRITICAL",
                    "rule_id": item["rule_id"],
                    "standard": item["standard"],
                    "requirement": item["requirement"],
                    "action": f"Immediately implement {item['requirement'].lower()}",
                    "deadline": "Within 30 days"
                })
        
        # Medium priority
        for item in findings["non_compliant"]:
            if item["priority"] == "MEDIUM":
                action_items.append({
                    "priority": "HIGH",
                    "rule_id": item["rule_id"],
                    "standard": item["standard"],
                    "requirement": item["requirement"],
                    "action": f"Plan and implement {item['requirement'].lower()}",
                    "deadline": "Within 60 days"
                })
        
        # Low priority
        for item in findings["non_compliant"]:
            if item["priority"] == "LOW":
                action_items.append({
                    "priority": "MEDIUM",
                    "rule_id": item["rule_id"],
                    "standard": item["standard"],
                    "requirement": item["requirement"],
                    "action": f"Schedule implementation of {item['requirement'].lower()}",
                    "deadline": "Within 90 days"
                })
        
        # Partial compliance items
        for item in findings["partial"]:
            action_items.append({
                "priority": "LOW",
                "rule_id": item["rule_id"],
                "standard": item["standard"],
                "requirement": item["requirement"],
                "action": f"Complete documentation for {item['requirement'].lower()}",
                "deadline": "Within 90 days"
            })
        
        return {
            "report_name": f"Compliance_Report_{filename}",
            "summary": {
                "compliance_score": check_result["compliance_score"],
                "status": self._get_compliance_status(check_result["compliance_score"]),
                "total_rules": check_result["total_rules_checked"],
                "compliant": check_result["compliant_count"],
                "partial": check_result["partial_count"],
                "non_compliant": check_result["non_compliant_count"]
            },
            "action_items": action_items[:10],  # Top 10 action items
            "standards_checked": list(findings["by_standard"].keys()),
            "high_priority_gaps": len([
                i for i in findings["non_compliant"] 
                if i["priority"] == "HIGH"
            ])
        }
    
    def _get_compliance_status(self, score: float) -> str:
        """Get compliance status based on score."""
        if score >= 80:
            return "COMPLIANT"
        elif score >= 60:
            return "PARTIALLY_COMPLIANT"
        elif score >= 40:
            return "NEEDS_IMPROVEMENT"
        else:
            return "NON_COMPLIANT"
    
    def get_available_standards(self) -> List[Dict]:
        """Get list of available compliance standards."""
        return [
            {
                "id": standard,
                "name": standard.replace("_", " "),
                "rule_count": len(rules)
            }
            for standard, rules in self.COMPLIANCE_RULES.items()
        ]