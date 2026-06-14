from openai import OpenAI
from env_var import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)