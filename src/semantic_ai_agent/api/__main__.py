"""Entry point: python -m semantic_ai_agent.api"""

import uvicorn

from semantic_ai_agent.settings import Settings

if __name__ == "__main__":
    uvicorn.run(
        "semantic_ai_agent.api.app:app",
        host=Settings.HOST,
        port=Settings.API_PORT,
        reload=True,
    )
