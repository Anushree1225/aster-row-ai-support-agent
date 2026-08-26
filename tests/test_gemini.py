import os

import pytest
from dotenv import load_dotenv
from google import genai


load_dotenv()


@pytest.mark.integration
def test_gemini_connection():
    """Optional live Gemini API connectivity test."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        pytest.skip("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Reply with exactly: Gemini connection successful!",
    )

    assert response.text.strip() == "Gemini connection successful!"