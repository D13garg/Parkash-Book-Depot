"""Reviews tools — 2 tools."""
from __future__ import annotations
from parkash_mcp.context import get_db, MCP_USER
from parkash_mcp.adapter import run_tool
from backend.app.services.review_service import ReviewService


def register_review_tools(mcp) -> None:

    @mcp.tool()
    async def list_reviews() -> str:
        """
        List all customer reviews across the platform (admin view).
        Returns all reviews with customer name, rating, category, message, and timestamp.
        """
        return await run_tool(ReviewService(get_db()).get_all_reviews, MCP_USER)

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
        return await run_tool(ReviewService(get_db()).delete_review, review_id, MCP_USER)