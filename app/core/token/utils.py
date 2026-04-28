
import tiktoken

from app.core.token.constants import DEFAULT_OPENAI_MODEL


class OpenAITokenUtil:
    @staticmethod
    def count_tokens(messages, model=DEFAULT_OPENAI_MODEL):
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0

        for message in messages:
            num_tokens += 4  # tokens de estructura por mensaje
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))

        num_tokens += 2  # tokens de priming
        return num_tokens