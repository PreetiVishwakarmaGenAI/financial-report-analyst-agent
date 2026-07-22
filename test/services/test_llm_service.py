import pytest   
from app.services.llm_service import LLMService


def test_llm_service():
    """
    Verify that the LLM service can initialize and generate a response.
    """

    llm_service = LLMService()

    response = llm_service.generate_response(
        role="planner",
        user_prompt="What is EBITDA?",
    )

    print("\nResponse")
    print("=" * 50)
    print(response)

    assert isinstance(response, str)
    assert len(response) > 0

def test_all_models():

    llm = LLMService()

    for role in [
        "planner",
        "researcher",
        "synthesizer",
    ]:

        response = llm.generate_response(
            role=role,
            user_prompt="Reply with only OK"
        )

        print(f"{role}: {response}")

        assert "OK" in response.upper()

def test_invalid_role():

    llm = LLMService()

    with pytest.raises(ValueError):

        llm.generate_response(
            role="invalid",
            user_prompt="Hello"
        )