"""
Main entry point for Country Info Agent CLI.
"""

import logging
import sys

from country_info_agent.logging_config import setup_logging
from country_info_agent.config import get_settings
from country_info_agent.services.agent_service import AgentService

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Country Info Agent CLI."""
    setup_logging()
    settings = get_settings()

    if not settings.google_api_key:
        logger.warning("GOOGLE_API_KEY not found. Agent may function in degraded mode.")

    service = AgentService()

    logger.info("Country Info Agent is ready!")
    logger.info(f"Health check: {service.health_check()}")

    while True:
        try:
            query = input("\nAsk a question about a country: ").strip()
            if query.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            if not query:
                continue

            result = service.process_query(query)

            if result.get("answer"):
                print(f"\nAssistant: {result['answer']}")
            elif result.get("error"):
                print(f"\nAssistant: {result['error']}")
            else:
                print("\nAssistant: I'm sorry, I couldn't provide an answer.")

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            print("\nAssistant: An unexpected error occurred. Please try again.")


if __name__ == "__main__":
    main()
