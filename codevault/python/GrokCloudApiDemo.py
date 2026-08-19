# Auto-generated Code Vault for 'GrokCloudApiDemo' [Python]

import os
import sys
from typing import Optional

import openai
from openai import OpenAI
from openai.types.chat.completion_create_response import ChatCompletionCreateResponse


class GrokCloudApiDemo:
    """
    Demonstrates how to make a basic API call to Grok Cloud using the OpenAI Python SDK.
    The request is sent to the base URL 'https://api.x.ai/v1' and uses the
    'llama-3.3-70b-versatile' model.

    The class can be instantiated with a custom API key or will read the key from the
    environment variable `OPENAI_API_KEY`. If no key is provided and the environment
    variable is missing, an exception will be raised.

    Example usage:
        demo = GrokCloudApiDemo()
        response = demo.send_message("Hello, world!")
        print(response)
    """

    MODEL = "llama-3.3-70b-versatile"
    BASE_URL = "https://api.x.ai/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the GrokCloudApiDemo client.

        Parameters
        ----------
        api_key : Optional[str]
            The API key for authenticating with Grok Cloud. If None, the key will
            be read from the `OPENAI_API_KEY` environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in the OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.api_key, base_url=self.BASE_URL)

    def send_message(self, message: str, temperature: float = 0.7) -> str:
        """
        Send a single message to the Grok Cloud model and return the text response.

        Parameters
        ----------
        message : str
            The prompt message to send to the model.
        temperature : float, optional
            Sampling temperature to use, by default 0.7.

        Returns
        -------
        str
            The content of the model's response.

        Raises
        ------
        openai.BadRequestError
            If the request fails due to an invalid request.
        """
        try:
            completion: ChatCompletionCreateResponse = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": message}],
                temperature=temperature,
                max_tokens=512,
            )
            # Extract the first choice's content
            content = completion.choices[0].message.content or ""
            return content.strip()
        except openai.OpenAIError as exc:
            # Log the error to stderr for visibility
            print(f"OpenAI API call failed: {exc}", file=sys.stderr)
            raise

    @staticmethod
    def main():
        """
        Main entry point for the script. Instantiates the demo and sends a test message.
        """
        demo = GrokCloudApiDemo()
        prompt = "Explain the concept of Grok Cloud in two sentences."
        print(f"Sending prompt to {GrokCloudApiDemo.MODEL}...\n")
        try:
            response = demo.send_message(prompt)
            print("Response:")
            print(response)
        except Exception as exc:
            print(f"An error occurred: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    GrokCloudApiDemo.main()
