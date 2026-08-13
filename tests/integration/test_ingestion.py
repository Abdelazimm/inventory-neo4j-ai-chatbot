import pytest
from app.services.graph_ingestion_service import GraphIngestionService


def test_graph_csv_preview_nodes():
    csv_data = b"label,id,name,properties\nAsset,TAG-777,Test Laptop,{}"
    preview = GraphIngestionService.preview_csv(csv_data, mode="nodes")
    assert preview["is_valid"] is True
    assert preview["total_rows"] == 1
    assert preview["missing_required_columns"] == []


def test_graph_csv_preview_relationships():
    csv_data = b"from_label,from_id,relationship_type,to_label,to_id\nVendor,V1,SUPPLIES,Item,ITM1"
    preview = GraphIngestionService.preview_csv(csv_data, mode="relationships")
    assert preview["is_valid"] is True
    assert preview["total_rows"] == 1
