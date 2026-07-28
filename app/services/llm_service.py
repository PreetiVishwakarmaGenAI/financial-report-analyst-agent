import logging
from typing import Type, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config.settings import settings
from app.enums.agent_role import AgentRole

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """
    Service responsible for interacting with Large Language Models.

    Responsibilities
    ----------------
    - Initialize LLMs
    - Generate text responses
    - Generate structured responses
    - Hide provider-specific implementation

    Business logic and prompts belong in the agents,
    not in this service.
    """

    def __init__(self) -> None:

        self.models = {
            AgentRole.PLANNER: self._initialize_llm(
                settings.PLANNER_MODEL
            ),
            AgentRole.RESEARCHER: self._initialize_llm(
                settings.RESEARCHER_MODEL
            ),
            AgentRole.SYNTHESIZER: self._initialize_llm(
                settings.SYNTHESIZER_MODEL
            ),
        }

    def _initialize_llm(
        self,
        model_name: str,
    ) -> BaseChatModel:
        """
        Initialize a chat model.
        """

        try:
            logger.info(
                "Initializing model '%s'...",
                model_name,
            )

            return ChatOpenAI(
                model=model_name,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.0,
                max_retries=2,
                timeout=60,
            )

        except Exception:
            logger.exception(
                "Failed to initialize model '%s'.",
                model_name,
            )
            raise

    def _get_model(
        self,
        role: AgentRole,
    ) -> BaseChatModel:
        """
        Return the configured model for a role.
        """

        try:
            return self.models[role]

        except KeyError:
            logger.error(
                "Unsupported LLM role '%s'",
                role,
            )

            raise ValueError(
                f"Unsupported role: {role}"
            )

    def _build_messages(
        self,
        user_prompt: str,
        system_prompt: str = "",
    ) -> list[BaseMessage]:
        """
        Construct LangChain messages.
        """

        messages: list[BaseMessage] = []

        if system_prompt:
            messages.append(
                SystemMessage(
                    content=system_prompt
                )
            )

        messages.append(
            HumanMessage(
                content=user_prompt
            )
        )

        return messages

    def generate_response(
        self,
        role: AgentRole,
        user_prompt: str,
        system_prompt: str = "",
    ) -> str:
        """
        Generate a text response.
        """

        llm = self._get_model(role)

        messages = self._build_messages(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )

        logger.info(
            "Generating response using role '%s'",
            role.value,
        )

        try:

            response = llm.invoke(messages)

            return response.content

        except Exception:
            logger.exception(
                "LLM invocation failed."
            )
            raise

    def generate_structured_response(
        self,
        role: AgentRole,
        user_prompt: str,
        response_model: Type[T],
        system_prompt: str = "",
    ) -> T:
        """
        Generate validated structured output.
        """

        llm = self._get_model(role)

        structured_llm = llm.with_structured_output(
            response_model
        )

        messages = self._build_messages(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )

        logger.info(
            "Generating structured response using role '%s'",
            role.value,
        )

        try:

            return structured_llm.invoke(messages)

        except Exception:
            logger.exception(
                "Structured LLM invocation failed."
            )
            raise