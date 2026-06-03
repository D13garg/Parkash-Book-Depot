from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import List
from app.schemas.analytics import (
    AnalyticsResponse, ExecutiveSummary, AssociatePerformance,
    ReviewMetrics, LowStockBook, StaleRequest, InactiveProject,
)


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_analytics(self) -> AnalyticsResponse:
        now = datetime.now(timezone.utc)

        # ── Executive Summary ─────────────────────────────────────────────
        total_requests  = await self.db["project_requests"].count_documents({})
        total_projects  = await self.db["projects"].count_documents({})
        completed       = await self.db["projects"].count_documents({"status": "completed"})
        total_reviews   = await self.db["reviews"].count_documents({})
        completion_rate = round(completed / total_projects * 100, 1) if total_projects > 0 else 0.0

        # low stock books
        low_stock_pipeline = [
            {"$match": {"is_active": True}},
            {"$match": {"$expr": {"$lte": ["$stock", "$low_stock_threshold"]}}},
            {"$count": "count"}
        ]
        low_stock_result = await self.db["books"].aggregate(low_stock_pipeline).to_list(1)
        low_stock_count = low_stock_result[0]["count"] if low_stock_result else 0

        # errors in last 24h
        error_count_24h = await self.db["error_logs"].count_documents({
            "created_at": {"$gte": now - timedelta(hours=24)}
        })

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
        converted = await self.db["project_requests"].count_documents({
            "status": {"$in": ["accepted", "converted_to_project"]}
        })
        conversion_rate = round(converted / total_requests * 100, 1) if total_requests > 0 else 0.0

        # ── Associate Performance ─────────────────────────────────────────
        associates_cursor = self.db["users"].find({"role": "associate", "is_active": True})
        associates = await associates_cursor.to_list(length=None)

        associate_perf: List[AssociatePerformance] = []
        for assoc in associates:
            aid = str(assoc["_id"])
            assigned  = await self.db["projects"].count_documents({"assigned_to": aid})
            completed_a = await self.db["projects"].count_documents({"assigned_to": aid, "status": "completed"})
            open_a    = await self.db["projects"].count_documents({
                "assigned_to": aid,
                "status": {"$in": ["assigned", "in_progress", "waiting_supplier"]}
            })

            # avg completion time from project_updates timeline
            avg_days = None
            completed_projects = await self.db["projects"].find(
                {"assigned_to": aid, "status": "completed"}
            ).to_list(length=None)

            if completed_projects:
                total_days = 0
                count = 0
                for p in completed_projects:
                    created = p.get("created_at")
                    updated = p.get("updated_at")
                    if created and updated:
                        diff = (updated - created).total_seconds() / 86400
                        total_days += diff
                        count += 1
                avg_days = round(total_days / count, 1) if count > 0 else None

            associate_perf.append(AssociatePerformance(
                associate_id=aid,
                associate_name=assoc.get("name", ""),
                associate_email=assoc.get("email", ""),
                assigned_projects=assigned,
                completed_projects=completed_a,
                open_projects=open_a,
                avg_completion_days=avg_days,
            ))

        # ── Review Metrics ────────────────────────────────────────────────
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        reviews_this_month = await self.db["reviews"].count_documents({
            "created_at": {"$gte": month_start}
        })

        avg_rating_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$rating"}}}]
        avg_result = await self.db["reviews"].aggregate(avg_rating_pipeline).to_list(1)
        avg_rating = round(avg_result[0]["avg"], 2) if avg_result else 0.0

        review_metrics = ReviewMetrics(
            average_rating=avg_rating,
            total_reviews=total_reviews,
            reviews_this_month=reviews_this_month,
        )

        # ── Low Stock Books ───────────────────────────────────────────────
        low_stock_cursor = self.db["books"].aggregate([
            {"$match": {"is_active": True}},
            {"$match": {"$expr": {"$lte": ["$stock", "$low_stock_threshold"]}}},
            {"$sort": {"stock": 1}},
            {"$limit": 5},
        ])
        low_stock_docs = await low_stock_cursor.to_list(length=5)
        low_stock_books = [
            LowStockBook(
                id=str(d["_id"]), title=d["title"],
                stock=d["stock"], low_stock_threshold=d["low_stock_threshold"],
            )
            for d in low_stock_docs
        ]

        # ── Stale Requests ────────────────────────────────────────────────
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

        # ── Inactive Projects ─────────────────────────────────────────────
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

        return AnalyticsResponse(
            summary=summary,
            request_conversion_rate=conversion_rate,
            associate_performance=associate_perf,
            review_metrics=review_metrics,
            low_stock_books=low_stock_books,
            stale_requests=stale_requests,
            inactive_projects=inactive_projects,
        )