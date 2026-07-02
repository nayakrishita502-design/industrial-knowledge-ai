import re
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    name: str
    node_type: str
    attributes: Dict = field(default_factory=dict)
    failures: List[Dict] = field(default_factory=list)
    maintenance: List[Dict] = field(default_factory=list)


@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph."""
    source: str
    target: str
    relationship: str
    metadata: Dict = field(default_factory=dict)


class KnowledgeGraph:
    """Build and manage industrial knowledge graph."""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
    
    def add_node(
        self, 
        node_id: str, 
        name: str, 
        node_type: str, 
        attributes: Optional[Dict] = None
    ) -> GraphNode:
        """Add or update a node."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            if attributes:
                node.attributes.update(attributes)
            return node
        
        node = GraphNode(
            id=node_id,
            name=name,
            node_type=node_type,
            attributes=attributes or {}
        )
        self.nodes[node_id] = node
        return node
    
    def add_edge(
        self, 
        source: str, 
        target: str, 
        relationship: str, 
        metadata: Optional[Dict] = None
    ) -> GraphEdge:
        """Add an edge between nodes."""
        edge = GraphEdge(
            source=source,
            target=target,
            relationship=relationship,
            metadata=metadata or {}
        )
        self.edges.append(edge)
        return edge
    
    def add_failure_record(self, node_id: str, failure_record: Dict):
        """Add a failure record to a node."""
        if node_id in self.nodes:
            self.nodes[node_id].failures.append({
                **failure_record,
                "timestamp": datetime.now().isoformat()
            })
    
    def add_maintenance_record(self, node_id: str, maintenance_record: Dict):
        """Add a maintenance record to a node."""
        if node_id in self.nodes:
            self.nodes[node_id].maintenance.append({
                **maintenance_record,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_connected_nodes(self, node_id: str) -> List[str]:
        """Get all nodes connected to a given node."""
        connected = set()
        for edge in self.edges:
            if edge.source == node_id:
                connected.add(edge.target)
            elif edge.target == node_id:
                connected.add(edge.source)
        return list(connected)
    
    def find_failure_patterns(self, node_id: str) -> Dict:
        """Analyze failure patterns for an equipment node."""
        node = self.nodes.get(node_id)
        if not node:
            return {"status": "not_found", "equipment": node_id}
        
        failures = node.failures
        if not failures:
            return {
                "status": "no_failures",
                "equipment": node_id,
                "equipment_name": node.name
            }
        
        # Group by failure type
        failure_types = {}
        for failure in failures:
            failure_type = failure.get("type", "unknown")
            if failure_type not in failure_types:
                failure_types[failure_type] = []
            failure_types[failure_type].append(failure)
        
        # Find most common failure
        most_common = max(failure_types.items(), key=lambda x: len(x[1]))
        
        return {
            "equipment": node_id,
            "equipment_name": node.name,
            "total_failures": len(failures),
            "failure_types": {k: len(v) for k, v in failure_types.items()},
            "most_common_failure": most_common[0],
            "most_common_count": len(most_common[1]),
            "most_recent": failures[-1] if failures else None,
            "maintenance_count": len(node.maintenance)
        }
    
    def export_for_visualization(self) -> Dict:
        """Export graph in vis.js compatible format."""
        nodes = []
        for node_id, node in self.nodes.items():
            # Determine color based on node state
            color = self._get_node_color(node)
            
            nodes.append({
                "id": node_id,
                "label": node.name,
                "type": node.node_type,
                "color": color,
                "title": self._get_node_tooltip(node),
                "shape": self._get_node_shape(node.node_type),
                "size": 25 + (len(node.failures) * 5)  # Larger if more failures
            })
        
        edges = []
        for edge in self.edges:
            edges.append({
                "from": edge.source,
                "to": edge.target,
                "label": edge.relationship.replace("_", " ").title(),
                "title": edge.relationship,
                "arrows": "to",
                "color": self._get_edge_color(edge.relationship)
            })
        
        return {"nodes": nodes, "edges": edges}
    
    def _get_node_color(self, node: GraphNode) -> str:
        """Determine node color based on state."""
        if node.failures:
            failure_count = len(node.failures)
            if failure_count >= 3:
                return "#e74c3c"  # Red - critical
            elif failure_count >= 1:
                return "#f39c12"  # Orange - warning
        return "#3498db"  # Blue - normal
    
    def _get_node_shape(self, node_type: str) -> str:
        """Get shape based on node type."""
        shapes = {
            "EQUIPMENT": "box",
            "PERSONNEL": "ellipse",
            "PROCEDURE": "diamond",
            "FAILURE": "triangle",
            "DATE": "dot"
        }
        return shapes.get(node_type.upper(), "box")
    
    def _get_node_tooltip(self, node: GraphNode) -> str:
        """Generate tooltip for node."""
        lines = [
            f"<b>{node.name}</b>",
            f"Type: {node.node_type}",
            f"Failures: {len(node.failures)}",
            f"Maintenance Records: {len(node.maintenance)}"
        ]
        if node.attributes:
            for k, v in node.attributes.items():
                lines.append(f"{k}: {v}")
        return "<br>".join(lines)
    
    def _get_edge_color(self, relationship: str) -> str:
        """Get edge color based on relationship type."""
        colors = {
            "FAILED_DUE_TO": "#e74c3c",
            "MAINTAINED_BY": "#27ae60",
            "CONNECTED_TO": "#3498db",
            "PART_OF": "#9b59b6",
            "INSPECTED_BY": "#f39c12"
        }
        return colors.get(relationship, "#95a5a6")
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        equipment_nodes = [n for n in self.nodes.values() if n.node_type == "EQUIPMENT"]
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "equipment_count": len(equipment_nodes),
            "total_failures": sum(len(n.failures) for n in self.nodes.values()),
            "total_maintenance": sum(len(n.maintenance) for n in self.nodes.values()),
            "nodes_with_failures": len([n for n in self.nodes.values() if n.failures])
        }


def build_graph_from_documents(documents: List[str]) -> KnowledgeGraph:
    """Build knowledge graph from parsed documents."""
    graph = KnowledgeGraph()
    
    # Equipment patterns
    equipment_patterns = [
        (r'(Compressor)\s+([A-Z]\d+)', "EQUIPMENT"),
        (r'(Pump)\s+([A-Z]?\d+[A-Z]?)', "EQUIPMENT"),
        (r'(Valve)\s+([A-Z]?\d+[A-Z]?)', "EQUIPMENT"),
        (r'(Motor)\s+([A-Z]?\d+[A-Z]?)', "EQUIPMENT"),
        (r'(Tank)\s+([A-Z]?\d+[A-Z]?)', "EQUIPMENT"),
        (r'(Turbine)\s+([A-Z]?\d+[A-Z]?)', "EQUIPMENT"),
        (r'(Generator)\s+([A-Z]?\d+[A-Z]?)', "EQUIPMENT"),
    ]
    
    # Personnel patterns
    personnel_patterns = [
        (r'(Technician\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "PERSONNEL"),
        (r'(Engineer\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "PERSONNEL"),
        (r'(Operator\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', "PERSONNEL"),
    ]
    
    for doc in documents:
        # Extract equipment
        for pattern, node_type in equipment_patterns:
            for match in re.finditer(pattern, doc, re.IGNORECASE):
                equipment_name = f"{match.group(1)} {match.group(2)}"
                node_id = f"{match.group(1).lower()}_{match.group(2).lower()}"
                graph.add_node(node_id, equipment_name, node_type)
        
        # Extract personnel
        for pattern, node_type in personnel_patterns:
            for match in re.finditer(pattern, doc):
                person_name = match.group(1)
                node_id = person_name.lower().replace(" ", "_")
                graph.add_node(node_id, person_name, node_type)
        
        # Extract failure relationships
        failure_patterns = [
            r'(\w+\s+\w+)\s+failed\s+(?:due to|caused by)\s+([^.!?]+)',
            r'failure\s+(?:of|in)\s+(\w+\s+\w+)\s+(?:due to|caused by)\s+([^.!?]+)',
        ]
        
        for pattern in failure_patterns:
            for match in re.finditer(pattern, doc, re.IGNORECASE):
                equipment = match.group(1).strip()
                cause = match.group(2).strip()
                
                # Find matching node
                equipment_lower = equipment.lower().replace(" ", "_")
                if equipment_lower in graph.nodes:
                    graph.add_failure_record(equipment_lower, {
                        "type": cause[:50],
                        "description": match.group(0)
                    })
        
        # Extract maintenance relationships
        maintenance_patterns = [
            r'(\w+\s+\w+)\s+(?:serviced|maintained|repaired)\s+by\s+([^.!?]+)',
            r'maintenance\s+(?:of|on)\s+(\w+\s+\w+)\s+by\s+([^.!?]+)',
        ]
        
        for pattern in maintenance_patterns:
            for match in re.finditer(pattern, doc, re.IGNORECASE):
                equipment = match.group(1).strip()
                technician = match.group(2).strip()
                
                equipment_id = equipment.lower().replace(" ", "_")
                technician_id = technician.lower().replace(" ", "_")[:30]
                
                if equipment_id in graph.nodes:
                    graph.add_maintenance_record(equipment_id, {
                        "technician": technician,
                        "description": match.group(0)
                    })
                    
                    # Add technician node if not exists
                    if technician_id not in graph.nodes:
                        graph.add_node(technician_id, technician[:30], "PERSONNEL")
                    
                    graph.add_edge(equipment_id, technician_id, "MAINTAINED_BY")
    
    return graph