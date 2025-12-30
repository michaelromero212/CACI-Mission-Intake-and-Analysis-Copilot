"""
Tests for Mission API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestMissionEndpoints:
    """Test suite for /api/missions endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_missions_empty(self, client: AsyncClient):
        """Test listing missions when database is empty."""
        response = await client.get("/api/missions")
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert data["total"] == 0
        assert len(data["missions"]) == 0
    
    @pytest.mark.asyncio
    async def test_submit_text_mission(self, client: AsyncClient, sample_text_submission: dict):
        """Test submitting a text mission."""
        response = await client.post("/api/missions/text", json=sample_text_submission)
        assert response.status_code == 200
        
        data = response.json()
        assert "mission_id" in data
        assert data["source_type"] == "text"
        assert data["status"] == "ingested"
        assert data["source_label"] == sample_text_submission["source_label"]
    
    @pytest.mark.asyncio
    async def test_get_mission_by_id(self, client: AsyncClient, sample_text_submission: dict):
        """Test retrieving a mission by ID."""
        # First create a mission
        create_response = await client.post("/api/missions/text", json=sample_text_submission)
        assert create_response.status_code == 200
        mission_id = create_response.json()["mission_id"]
        
        # Then retrieve it
        get_response = await client.get(f"/api/missions/{mission_id}")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["mission_id"] == mission_id
        assert data["source_label"] == sample_text_submission["source_label"]
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_mission(self, client: AsyncClient):
        """Test 404 for non-existent mission."""
        response = await client.get("/api/missions/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_mission(self, client: AsyncClient, sample_text_submission: dict):
        """Test deleting a mission."""
        # Create a mission
        create_response = await client.post("/api/missions/text", json=sample_text_submission)
        mission_id = create_response.json()["mission_id"]
        
        # Delete it
        delete_response = await client.delete(f"/api/missions/{mission_id}")
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = await client.get(f"/api/missions/{mission_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_upload_csv_file(self, client: AsyncClient, sample_csv_content: bytes):
        """Test uploading a CSV file."""
        files = {"file": ("test_threats.csv", sample_csv_content, "text/csv")}
        response = await client.post("/api/missions/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["source_type"] == "csv"
        assert data["filename"] == "test_threats.csv"
        assert data["status"] == "ingested"
    
    @pytest.mark.asyncio
    async def test_upload_txt_file(self, client: AsyncClient, sample_txt_content: bytes):
        """Test uploading a TXT file."""
        files = {"file": ("analyst_notes.txt", sample_txt_content, "text/plain")}
        response = await client.post("/api/missions/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["source_type"] == "text"
        assert data["filename"] == "analyst_notes.txt"
    
    @pytest.mark.asyncio
    async def test_upload_unsupported_file(self, client: AsyncClient):
        """Test rejection of unsupported file types."""
        files = {"file": ("malware.exe", b"bad content", "application/octet-stream")}
        response = await client.post("/api/missions/upload", files=files)
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_list_missions_with_data(self, client: AsyncClient, sample_text_submission: dict):
        """Test listing missions after creating some."""
        # Create 3 missions
        for i in range(3):
            submission = {**sample_text_submission, "source_label": f"Mission {i+1}"}
            await client.post("/api/missions/text", json=submission)
        
        # List all
        response = await client.get("/api/missions")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3
        assert len(data["missions"]) == 3
