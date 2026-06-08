"""OpenAPI request body examples for cache routes."""

from fastapi.openapi.models import Example

from semantic_ai_agent.api.schema import HydrateRequest

EXAMPLES: dict[str, Example] = {
    "default_path": {
        "summary": "Default FAQ path",
        "description": "Hydrate from the bundled **data/raw/faq_data.json** file (no path needed).",
        "value": HydrateRequest.create_example().model_dump(),
    },
    "custom_path": {
        "summary": "Custom FAQ path",
        "description": "Hydrate from a **custom** JSON file on the server filesystem.",
        "value": HydrateRequest.create_example(faq_path="data/raw/faq_data.json").model_dump(),
    },
}
