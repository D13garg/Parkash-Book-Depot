import asyncio
import time
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List
from app.schemas.analytics import (
    AnalyticsResponse, ExecutiveSummary, AssociatePerformance,
    ReviewMetrics, LowStockBook, StaleRequest, InactiveProject,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_analytics(self) -> AnalyticsResponse:
        perf_total_start = time.perf_counter()
        now = datetime.now(timezone.utc)

        # ── Executive Summary ─────────────────────────────────────────────
        perf_summary_start = time.perf_counter()
        logger.info("[PERF] ANALYTICS: Starting executive summary queries...")
        
        # Parallelize all independent count queries for better performance
        (total_requests, total_projects, completed, total_reviews, error_count_24h) = await asyncio.gather(
            self.db["project_requests"].count_documents({}),
            self.db["projects"].count_documents({}),
            self.db["projects"].count_documents({"status": "completed"}),
            self.db["reviews"].count_documents({}),
            self.db["error_logs"].count_documents({
                "created_at": {"$gte": now - timedelta(hours=24)}
            }),
        )
        
        completion_rate = round(completed / total_projects * 100, 1) if total_projects > 0 else 0.0
        perf_summary_elapsed = time.perf_counter() - perf_summary_start
        logger.info(f"[PERF] ANALYTICS SUMMARY: {perf_summary_elapsed:.3f}s (5 parallel queries)")

        # ── Low Stock Query ──────────────────────────────────────────────
        perf_lowstock_start = time.perf_counter()
        logger.debug("[PERF] ANALYTICS: Starting low stock aggregation...")
        
        # Low stock count with facet to get both count and details in single query
        low_stock_pipeline = [
            {"$match": {"is_active": True}},
            {"$match": {"$expr": {"$lte": ["$stock", "$low_stock_threshold"]}}},
            {"$facet": {
                "metadata": [{"$count": "total"}],
                "books": [
                    {"$sort": {"stock": 1}},
                    {"$limit": 5},
                    {"$project": {"_id": 1, "title": 1, "stock": 1, "low_stock_threshold": 1}}
                ]
            }}
        ]
        low_stock_result = await self.db["books"].aggregate(low_stock_pipeline).to_list(1)
        low_stock_count = low_stock_result[0]["metadata"][0]["total"] if low_stock_result and low_stock_result[0]["metadata"] else 0
        low_stock_docs = low_stock_result[0]["books"] if low_stock_result else []
        perf_lowstock_elapsed = time.perf_counter() - perf_lowstock_start
        logger.info(f"[PERF] ANALYTICS LOW_STOCK: {perf_lowstock_elapsed:.3f}s (count={low_stock_count}, books={len(low_stock_docs)})")

        summary = ExecutiveSummary(
            total_requests=total_requests,
            total_projects=total_projects,
            completed_projects=completed,
            completion_rate_percent=completion_rate,
            total_reviews=total_reviews,
            low_stock_count=low_stock_count,
            error_count_24h=error_count_24h,
        )

        # ── Request Conversion Rate ───────────────────────────────────────
        perf_conversion_start = time.perf_counter()
        logger.debug("[PERF] ANALYTICS: Starting conversion rate query...")
        
        converted = await self.db["project_requests"].count_documents({
            "status": {"$in": ["accepted", "converted_to_project"]}
        })
        conversion_rate = round(converted / total_requests * 100, 1) if total_requests > 0 else 0.0
        perf_conversion_elapsed = time.perf_counter() - perf_conversion_start
        logger.info(f"[PERF] ANALYTICS CONVERSION: {perf_conversion_elapsed:.3f}s (rate={conversion_rate}%)")

        # ── Associate Performance (Single aggregation instead of N+1 queries) ─
        # CRITICAL FIX: Convert ObjectId to string for $lookup match
        # users._id is ObjectId, projects.assigned_to is string
        # NOTE: If this aggregation is slow with many associates/projects, consider:
        # - Adding compound indexes on (assigned_to, status)
        # - Caching results for 1-5 minutes
        # - Paginating results if needed
        perf_associates_start = time.perf_counter()
        logger.info("[PERF] ANALYTICS: Starting associate performance aggregation...")
        logger.debug("[PERF] ANALYTICS: WARNING - Large $lookup with complex $let/$map may be slow with large datasets")
        
        pipeline = [
            {"$match": {"role": "associate", "is_active": True}},
            {"$lookup": {
                "from": "projects",
                "let": {"userId": {"$toString": "$_id"}},  # Convert ObjectId to string
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$assigned_to", "$$userId"]}}},
                ],
                "as": "projects"
            }},
            {"$addFields": {
                "assigned_projects": {"$size": "$projects"},
                "completed_projects": {
                    "$size": {
                        "$filter": {
                            "input": "$projects",
                            "as": "proj",
                            "cond": {"$eq": ["$$proj.status", "completed"]}
                        }
                    }
                },
                "open_projects": {
                    "$size": {
                        "$filter": {
                            "input": "$projects",
                            "as": "proj",
                            "cond": {"$in": ["$$proj.status", ["assigned", "in_progress", "waiting_supplier"]]}
                        }
                    }
                },
                "avg_completion_days": {
                    "$let": {
                        "vars": {
                            "completed": {
                                "$filter": {
                                    "input": "$projects",
                                    "as": "proj",
                                    "cond": {"$eq": ["$$proj.status", "completed"]}
                                }
                            }
                        },
                        "in": {
                            "$cond": [
                                {"$eq": [{"$size": "$$completed"}, 0]},
                                None,
                                {
                                    "$round": [
                                        {
                                            "$divide": [
                                                {
                                                    "$sum": {
                                                        "$map": {
                                                            "input": "$$completed",
                                                            "as": "proj",
                                                            "in": {
                                                                "$divide": [
                                                                    {"$subtract": ["$$proj.updated_at", "$$proj.created_at"]},
                                                                    86400000
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {"$size": "$$completed"}
                                            ]
                                        },
                                        1
                                    ]
                                }
                            ]
                        }
                    }
                }
            }},
            {"$project": {
                "associate_id": {"$toString": "$_id"},
                "associate_name": "$name",
                "associate_email": "$email",
                "assigned_projects": 1,
                "completed_projects": 1,
                "open_projects": 1,
                "avg_completion_days": 1,
            }}
        ]

        associate_perf: List[AssociatePerformance] = []
        async for doc in self.db["users"].aggregate(pipeline):
            associate_perf.append(AssociatePerformance(
                associate_id=doc["associate_id"],
                associate_name=doc["associate_name"],
                associate_email=doc["associate_email"],
                assigned_projects=doc["assigned_projects"],
                completed_projects=doc["completed_projects"],
                open_projects=doc["open_projects"],
                avg_completion_days=doc["avg_completion_days"],
            ))
        
        perf_associates_elapsed = time.perf_counter() - perf_associates_start
        logger.info(f"[PERF] ANALYTICS ASSOCIATES: {perf_associates_elapsed:.3f}s ({len(associate_perf)} associates with $lookup)")

        # ── Review Metrics ────────────────────────────────────────────────
        perf_reviews_start = time.perf_counter()
        logger.debug("[PERF] ANALYTICS: Starting review metrics queries...")
        
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Parallelize review metrics queries
        (reviews_this_month, avg_rating) = await asyncio.gather(
            self.db["reviews"].count_documents({"created_at": {"$gte": month_start}}),
            self._get_average_rating(),
        )

        review_metrics = ReviewMetrics(
            average_rating=avg_rating,
            total_reviews=total_reviews,
            reviews_this_month=reviews_this_month,
        )
        
        perf_reviews_elapsed = time.perf_counter() - perf_reviews_start
        logger.info(f"[PERF] ANALYTICS REVIEWS: {perf_reviews_elapsed:.3f}s (2 parallel queries)")

        # ── Low Stock Books (already fetched above with facet) ──────────────
        low_stock_books = [
            LowStockBook(
                id=str(d["_id"]), title=d["title"],
                stock=d["stock"], low_stock_threshold=d["low_stock_threshold"],
            )
            for d in low_stock_docs
        ]

        # ── Stale Requests ────────────────────────────────────────────────
        perf_stale_start = time.perf_counter()
        logger.debug("[PERF] ANALYTICS: Starting stale requests query...")
        
        stale_cutoff = now - timedelta(days=7)
        stale_cursor = self.db["project_requests"].find({
            "status": {"$in": ["submitted", "under_review"]},
            "created_at": {"$lte": stale_cutoff},
        }).sort("created_at", 1).limit(20)
        stale_docs = await stale_cursor.to_list(length=20)
        stale_requests = [
            StaleRequest(
                id=str(d["_id"]), title=d["title"],
                category=d.get("category", ""),
                status=d["status"],
                days_old=int((now - d["created_at"].replace(tzinfo=timezone.utc) 
                              if d["created_at"].tzinfo is None 
                              else now - d["created_at"]).total_seconds() / 86400),
                customer_id=d["customer_id"],
            )
            for d in stale_docs
        ]
        
        perf_stale_elapsed = time.perf_counter() - perf_stale_start
        logger.info(f"[PERF] ANALYTICS STALE_REQUESTS: {perf_stale_elapsed:.3f}s ({len(stale_requests)} requests)")

        # ── Inactive Projects ─────────────────────────────────────────────
        perf_inactive_start = time.perf_counter()
        logger.debug("[PERF] ANALYTICS: Starting inactive projects query...")
        
        inactive_cutoff = now - timedelta(days=14)
        inactive_cursor = self.db["projects"].find({
            "status": "in_progress",
            "updated_at": {"$lte": inactive_cutoff},
        }).sort("updated_at", 1).limit(20)
        inactive_docs = await inactive_cursor.to_list(length=20)
        inactive_projects = [
            InactiveProject(
                id=str(d["_id"]), title=d["title"],
                status=d["status"],
                assigned_to=d.get("assigned_to"),
                days_since_update=int((now - (d["updated_at"].replace(tzinfo=timezone.utc)
                                              if d["updated_at"].tzinfo is None
                                              else d["updated_at"])).total_seconds() / 86400),
            )
            for d in inactive_docs
        ]
        
        perf_inactive_elapsed = time.perf_counter() - perf_inactive_start
        logger.info(f"[PERF] ANALYTICS INACTIVE_PROJECTS: {perf_inactive_elapsed:.3f}s ({len(inactive_projects)} projects)")

        perf_total_elapsed = time.perf_counter() - perf_total_start
        logger.info(
            f"[PERF] ANALYTICS TOTAL: {perf_total_elapsed:.3f}s "
            f"(summary={perf_summary_elapsed:.3f}s, low_stock={perf_lowstock_elapsed:.3f}s, "
            f"conversion={perf_conversion_elapsed:.3f}s, associates={perf_associates_elapsed:.3f}s, "
            f"reviews={perf_reviews_elapsed:.3f}s, stale={perf_stale_elapsed:.3f}s, "
            f"inactive={perf_inactive_elapsed:.3f}s)"
        )

        return AnalyticsResponse(
            summary=summary,
            request_conversion_rate=conversion_rate,
            associate_performance=associate_perf,
            review_metrics=review_metrics,
            low_stock_books=low_stock_books,
            stale_requests=stale_requests,
            inactive_projects=inactive_projects,
        )

    async def _get_average_rating(self) -> float:
        """
        Extract average rating calculation to separate method.
        Includes timing instrumentation.
        """
        perf_start = time.perf_counter()
        logger.debug("[PERF] ANALYTICS: Starting average rating aggregation...")
        
        avg_rating_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$rating"}}}]
        avg_result = await self.db["reviews"].aggregate(avg_rating_pipeline).to_list(1)
        result = round(avg_result[0]["avg"], 2) if avg_result else 0.0
        
        perf_elapsed = time.perf_counter() - perf_start
        logger.debug(f"[PERF] ANALYTICS AVG_RATING: {perf_elapsed:.3f}s (result={result})")
        
        return result