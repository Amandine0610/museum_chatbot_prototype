"""
test_rag_pipeline.py
Unit tests for the Rwandan Museum Chatbot ML Service.
Tests the RAG pipeline logic using mock data (no API key required).
Run with: python test_rag_pipeline.py
"""

import unittest
import sys
import os

# Add parent directory to path so we can import rag_pipeline
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestMockRAGPipeline(unittest.TestCase):
    """Tests for the RAG pipeline running in mock/demo mode."""

    def setUp(self):
        """Import get_answer after ensuring no API key is set for mock mode."""
        # Temporarily unset API key to force mock mode
        self.original_key = os.environ.pop("OPENAI_API_KEY", None)
        from rag_pipeline import get_answer, initialize_rag
        initialize_rag()
        self.get_answer = get_answer

    def tearDown(self):
        if self.original_key:
            os.environ["OPENAI_API_KEY"] = self.original_key

    def test_mock_response_not_empty(self):
        """Mock mode should always return a non-empty string."""
        response = self.get_answer("What is the Ingoma?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_mock_response_contains_query(self):
        """Mock response should echo back the user query."""
        query = "Tell me about the Royal Drum"
        response = self.get_answer(query)
        self.assertIn(query, response)

    def test_mock_response_mentions_demo_mode(self):
        """Mock response should indicate demo mode is active."""
        response = self.get_answer("What museums are in Rwanda?")
        self.assertIn("Demo Mode", response)

    def test_empty_query_handled(self):
        """Empty string query should still return a string, not crash."""
        response = self.get_answer("")
        self.assertIsInstance(response, str)

    def test_multilingual_query_english(self):
        """English query should work without errors."""
        response = self.get_answer("What is the significance of Ingoma drums?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_multilingual_query_french(self):
        """French query should work without errors."""
        response = self.get_answer("Quelle est la signification des tambours Ingoma?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_multilingual_query_kinyarwanda(self):
        """Kinyarwanda query should work without errors."""
        response = self.get_answer("Ingoma ni iki mu muco w'u Rwanda?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_response_time_reasonable(self):
        """Response should be generated quickly in mock mode (< 2 seconds)."""
        import time
        start = time.time()
        self.get_answer("What artefacts are in the Ethnographic Museum?")
        elapsed = time.time() - start
        self.assertLess(elapsed, 2.0, "Mock response took too long")


class TestFlaskAPI(unittest.TestCase):
    """Integration tests for the Flask REST API endpoints."""

    def setUp(self):
        os.environ.pop("OPENAI_API_KEY", None)
        from app import app
        app.testing = True
        self.client = app.test_client()

    def test_health_endpoint_returns_200(self):
        """GET /health should return 200 with healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_query_endpoint_returns_response(self):
        """POST /query with valid body should return a response string."""
        response = self.client.post(
            "/query",
            json={"query": "What is the Royal Drum?", "language": "en"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("response", data)
        self.assertIsInstance(data["response"], str)

    def test_query_endpoint_missing_body_returns_400(self):
        """POST /query with no body should return 400 error."""
        response = self.client.post("/query", json={}, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_query_endpoint_french_language(self):
        """POST /query with French language tag should succeed."""
        response = self.client.post(
            "/query",
            json={"query": "Qu'est-ce que l'Ingoma?", "language": "fr"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["language"], "fr")

    def test_query_endpoint_kinyarwanda_language(self):
        """POST /query with Kinyarwanda language tag should succeed."""
        response = self.client.post(
            "/query",
            json={"query": "Ingoma ni iki?", "language": "rw"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["language"], "rw")


if __name__ == "__main__":
    print("=" * 60)
    print("Rwandan Museum Chatbot — ML Service Test Suite")
    print("=" * 60)
    unittest.main(verbosity=2)
