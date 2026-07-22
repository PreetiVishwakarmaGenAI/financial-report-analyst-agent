import logging

# from langchain_anthropic import ChatAnthropic
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service responsible for interacting with the Large Language Model.

    Responsibilities
    ----------------
    - Initialize the LLM
    - Generate responses
    - Centralize model configuration
    - Hide the underlying provider from the rest of the application

    This abstraction makes it easy to:
    - Switch models
    - Add retries
    - Add streaming
    - Add tool calling
    - Track token usage
    """

    FINANCIAL_ANALYST_SYSTEM_PROMPT = """
    You are an expert financial analyst.

    Answer ONLY using the provided context.

    If the answer cannot be found in the context,
    say that the information is not available.

    Do not hallucinate.

    Always answer in a clear and professional manner.
    """

    def __init__(self) -> None:
        self.models = {
            "planner": self._initialize_llm(settings.PLANNER_MODEL),
            "researcher": self._initialize_llm(settings.RESEARCHER_MODEL),
            "synthesizer": self._initialize_llm(settings.SYNTHESIZER_MODEL),
        }
    def _initialize_llm(self, model_name: str) -> ChatOpenAI:
        """
        Initialize the LangChain OpenAI model.
        """

        try:
            logger.info(
                "Initializing LLM '%s'...",
                model_name,
            )

            llm = ChatOpenAI(
                model=model_name,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.0,
            )
            return llm

        except Exception:
            logger.exception("Failed to initialize LLM.")
            raise
    
    def answer_question(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Answer a user question using the retrieved context.

        Args:
            question: User question.
            context: Context retrieved from the vector database.

        Returns:
            Generated answer.
        """

        prompt = f"""
        Context:
        {context}

        ----------------------------------------

        Question:
        {question}

        Answer:
        """

        return self.generate_response(
            role="planner",
            user_prompt=prompt,
            system_prompt=self.FINANCIAL_ANALYST_SYSTEM_PROMPT,
        )

    def generate_response(
        self,
        role: str,
        user_prompt: str,
        system_prompt: str = "",
    ) -> str:
        """
        Generate a response from the language model.

        Args:
            user_prompt:
                User question.

            system_prompt:
                Instructions for the model.

        Returns:
            Generated response.
        """

        try:
            try:
                llm = self.models[role]
            except KeyError:
                logger.error("Unsupported LLM role: %s", role)
                raise ValueError(f"Unsupported role: {role}")
            messages = []

            if system_prompt:
                messages.append(
                    SystemMessage(content=system_prompt)
                )

            messages.append(
                HumanMessage(content=user_prompt)
            )

            response = llm.invoke(messages)

            logger.info("Response generated successfully.")

            return response.content

        except Exception:
            logger.exception(
                "Failed to generate response."
            )
            raise