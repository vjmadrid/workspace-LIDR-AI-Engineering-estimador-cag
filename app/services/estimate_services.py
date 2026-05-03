import logging

from openai import OpenAI

from app.config import get_settings
from app.constants.estimate_constants import OPENAI_MODEL_DEFAULT
from app.core.cost.utils import OpenAICostUtil
from app.core.token.utils import OpenAITokenUtil
from app.dtos.estimate_dtos import EstimateResponseDTO
from app.exceptions.estimate_exceptions import EstimateServiceException
from app.services.estimate_prompt_builder import EstimatePromptBuilder

logger = logging.getLogger(__name__)


class EstimateService:
    def __init__(
        self,
        client: OpenAI | None = None,
        prompt_builder: EstimatePromptBuilder | None = None,
        settings=None,
    ):
        self._client = client
        self._settings = settings or get_settings()
        self._prompt_builder = prompt_builder or EstimatePromptBuilder()

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self._settings.OPENAI_API_KEY)
        return self._client

    def estimate_from_transcript(
        self,
        transcript: str,
        model: str = OPENAI_MODEL_DEFAULT,
    ) -> EstimateResponseDTO:
        messages = self._prompt_builder.build_messages(transcript)

        logger.info("Estimating transcript with model=%s", model)
        input_tokens = OpenAITokenUtil.count_tokens(messages, model)
        logger.debug("Estimated prompt tokens: %s", input_tokens)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
            )
        except Exception as exc:
            logger.exception("Error while generating estimation")
            raise EstimateServiceException(
                "An error occurred while generating the estimation"
            ) from exc

        if response.usage is None:
            raise EstimateServiceException(
                "The LLM response did not include token usage metadata"
            )

        response_content = response.choices[0].message.content
        if not response_content:
            raise EstimateServiceException("The LLM response content is empty")

        logger.debug("Prompt tokens used: %s", response.usage.prompt_tokens)
        logger.debug("Completion tokens used: %s", response.usage.completion_tokens)
        logger.debug("Total tokens used: %s", response.usage.total_tokens)

        token_costs = OpenAICostUtil.calculate_cost(
            model=model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
        )

        return EstimateResponseDTO(
            llm_provider=self._settings.LLM_PROVIDER,
            llm_model=model,
            response=response_content.strip(),
            num_tokens_input=response.usage.prompt_tokens,
            num_tokens_response=response.usage.completion_tokens,
            num_tokens_total=response.usage.total_tokens,
            input_token_cost=token_costs.input_token_cost,
            output_token_cost=token_costs.output_token_cost,
            total_token_cost=token_costs.total_token_cost,
        )
