import fal_client



async def generate_response(prompt: str)->str:
    handler = await fal_client.submit_async(
        "fal-ai/any-llm",
        arguments={
            "prompt": prompt,
            "model": "anthropic/claude-3.5-sonnet",
        },
    )

    result = await handler.get()

    return result["output"]