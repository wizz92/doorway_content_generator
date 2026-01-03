"""Tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app
from app.database import SessionLocal, Job, init_db, Base, engine
import uuid


# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Setup test database before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAPIRoutes:
    """Test cases for API routes."""
    
    def test_upload_csv_valid(self):
        """Test uploading a valid CSV file."""
        csv_content = "keyword\nkeyword1\nkeyword2\nkeyword3"
        files = {"file": ("test.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
        
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["keywords_count"] == 3
        assert len(data["preview"]) == 3
    
    def test_upload_csv_invalid_format(self):
        """Test uploading a non-CSV file."""
        files = {"file": ("test.txt", BytesIO(b"not a csv"), "text/plain")}
        
        response = client.post("/api/upload", files=files)
        
        assert response.status_code == 400
    
    def test_generate_content(self):
        """Test starting content generation."""
        # First create a job
        csv_content = "keyword\nkeyword1\nkeyword2"
        files = {"file": ("test.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
        upload_response = client.post("/api/upload", files=files)
        job_id = upload_response.json()["job_id"]
        
        # Then generate
        generate_data = {
            "job_id": job_id,
            "lang": "hu",
            "geo": "HU",
            "num_websites": 2
        }
        
        response = client.post("/api/generate", json=generate_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "job_id" in data
    
    def test_get_job_status(self):
        """Test getting job status."""
        # Create a job
        csv_content = "keyword\nkeyword1"
        files = {"file": ("test.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
        upload_response = client.post("/api/upload", files=files)
        job_id = upload_response.json()["job_id"]
        
        response = client.get(f"/api/job/{job_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] in ["queued", "processing", "completed", "failed"]
    
    def test_get_job_status_not_found(self):
        """Test getting status of non-existent job."""
        fake_job_id = str(uuid.uuid4())
        
        response = client.get(f"/api/job/{fake_job_id}/status")
        
        assert response.status_code == 404
    
    def test_list_jobs(self):
        """Test listing jobs."""
        response = client.get("/api/jobs")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Multi-Website Content Generator" in response.text

