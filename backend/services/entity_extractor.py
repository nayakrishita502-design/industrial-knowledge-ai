import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float = 1.0


class EntityExtractor:
    """Extract industrial entities from text."""
    
    ENTITY_PATTERNS = {
        "EQUIPMENT": [
            (r'\b(Compressor)\s+([A-Z]\d+)\b', 0.95),
            (r'\b(Pump)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Valve)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Motor)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Tank)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Turbine)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Generator)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Boiler)\s+([A-Z]?\d+[A-Z]?)\b', 0.95),
            (r'\b(Heat\s*Exchanger)\s+([A-Z]?\d+[A-Z]?)\b', 0.90),
            (r'\b([A-Z]{2,4}[-_]\d{4,6})\b', 0.85),  # Equipment codes
        ],
        "DATE": [
            (r'\b(\d{4}-\d{2}-\d{2})\b', 0.99),
            (r'\b(\d{2}/\d{2}/\d{4})\b', 0.95),
            (r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b', 0.90),
        ],
        "PROCEDURE": [
            (r'\b(SOP[-\s]?\d+)\b', 0.95),
            (r'\b(Procedure\s+\d+)\b', 0.90),
            (r'\b(Work\s+Order\s+\d+)\b', 0.90),
            (r'\b(WO[-\s]?\d+)\b', 0.90),
        ],
        "MEASUREMENT": [
            (r'\b(\d+(?:\.\d+)?\s*(?:PSI|psi|bar|Bar|BAR))\b', 0.95),
            (r'\b(\d+(?:\.\d+)?\s*(?:°[CF]|degrees?\s*[CF]))\b', 0.95),
            (r'\b(\d+(?:\.\d+)?\s*(?:RPM|rpm))\b', 0.95),
            (r'\b(\d+(?:\.\d+)?\s*(?:GPM|gpm|L/min))\b', 0.90),
            (r'\b(\d+(?:\.\d+)?\s*(?:kW|MW|HP|hp))\b', 0.90),
        ],
        "FAILURE_MODE": [
            (r'\b(seal\s+failure)\b', 0.90),
            (r'\b(bearing\s+failure)\b', 0.90),
            (r'\b(overheating)\b', 0.85),
            (r'\b(vibration)\b', 0.80),
            (r'\b(leakage|leak)\b', 0.85),
            (r'\b(corrosion)\b', 0.85),
            (r'\b(fatigue\s+crack)\b', 0.90),
            (r'\b(electrical\s+fault)\b', 0.90),
        ],
        "PERSONNEL": [
            (r'\b(Technician\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', 0.90),
            (r'\b(Engineer\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', 0.90),
            (r'\b(Operator\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', 0.90),
        ],
    }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all entities from text."""
        entities = []
        
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern, confidence in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = Entity(
                        text=match.group(0),
                        entity_type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence
                    )
                    entities.append(entity)
        
        # Remove duplicates and overlapping entities
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate and overlapping entities, keeping highest confidence."""
        if not entities:
            return []
        
        # Sort by start position, then by confidence (descending)
        entities.sort(key=lambda e: (e.start, -e.confidence))
        
        result = []
        last_end = -1
        
        for entity in entities:
            if entity.start >= last_end:
                result.append(entity)
                last_end = entity.end
            elif entity.confidence > result[-1].confidence:
                result[-1] = entity
                last_end = entity.end
        
        return result
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Dict]:
        """Extract relationships between entities."""
        relationships = []
        
        # Failure relationships
        failure_patterns = [
            r'(\w+\s+\w+)\s+(?:failed|failure)\s+(?:due to|caused by|because of)\s+([^.!?]+)',
            r'(\w+\s+\w+)\s+(?:was|were)\s+(?:damaged|affected)\s+by\s+([^.!?]+)',
        ]
        
        for pattern in failure_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                relationships.append({
                    "source": match.group(1).strip(),
                    "target": match.group(2).strip(),
                    "relationship": "FAILED_DUE_TO",
                    "context": match.group(0)
                })
        
        # Maintenance relationships
        maintenance_patterns = [
            r'(\w+\s+\w+)\s+(?:serviced|maintained|repaired)\s+by\s+([^.!?]+)',
            r'(\w+\s+\w+)\s+(?:replaced|installed)\s+on\s+(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in maintenance_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                relationships.append({
                    "source": match.group(1).strip(),
                    "target": match.group(2).strip(),
                    "relationship": "MAINTAINED_BY",
                    "context": match.group(0)
                })
        
        return relationships
    
    def to_dict(self, entities: List[Entity]) -> List[Dict]:
        """Convert entities to dictionary format."""
        return [
            {
                "text": e.text,
                "type": e.entity_type,
                "start": e.start,
                "end": e.end,
                "confidence": e.confidence
            }
            for e in entities
        ]