import pytest
from unittest.mock import patch, MagicMock
from chatgpt import generate_names_chat, draft_email_chat

@pytest.fixture
def mock_response_generate():
    mock_choice = MagicMock()
    mock_choice.message.content = "Name One\nName Two\nName Three"
    return [mock_choice]

@pytest.fixture
def mock_response_email():
    mock_choice = MagicMock()
    mock_choice.message.content = "Dear Jesse,\n\nHere is the agenda overview and team introductions..."
    return [mock_choice]


@patch("chatgpt.client.chat.completions.create")
def test_generate_names_chat(mock_create, mock_response_generate):
    mock_create.return_value.choices = mock_response_generate
    result = generate_names_chat("futuristic cities", number_of_names=3)
    assert len(result) == 3
    assert "Name One" in result


@patch("chatgpt.client.chat.completions.create")
def test_draft_email_chat(mock_create, mock_response_email):
    mock_create.return_value.choices = mock_response_email
    result = draft_email_chat(
        recipient="Jesse",
        topic="Final Project",
        main_points=["Overview", "Goals", "Deadline"],
        tone="friendly"
    )
    assert result.startswith("Dear Jesse")
    assert "overview" in result.lower() or "goals" in result.lower()
