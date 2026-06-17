"""Reviews tools — 2 tools. Calls the backend over HTTP instead of MongoDB."""
from __future__ import annotations
from parkash_mcp.context import get_client
from parkash_mcp.adapter import run_tool


def register_review_tools(mcp) -> None:

    @mcp.tool()
    async def list_reviews() -> str:
        """
        List all customer reviews across the platform (admin view).
        Returns all reviews with customer name, rating, category, message, and timestamp.
        """
        return await run_tool(get_client().get, "/reviews")

    @mcp.tool()
    async def delete_review(review_id: str, confirm: bool = False) -> str:
        """
        Delete a customer review. This action is irreversible.
        Requires confirm=True to prevent accidental deletion by AI clients.
        Args:
            review_id: MongoDB ObjectId string of the review.
            confirm: Must be explicitly set to True to proceed.
        """
        if not confirm:
            return (
                "ERROR [CONFIRMATION_REQUIRED]: Set confirm=True to delete this review. "
                "This action is irreversible."
            )
        return await run_tool(get_client().delete, f"/reviews/{review_id}")
