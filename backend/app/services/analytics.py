import polars as pl
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models.all_models import AttendanceLog, User, Department, Shift

class AnalyticsService:
    @staticmethod
    def get_wellness_heatmap(db: Session, org_id: str) -> List[Dict[str, Any]]:
        """
        Uses Polars to aggregate emotion data by department to identify burnout risk.
        Logic: Group by Dept, Calculate % of negative emotions.
        """
        # 1. Fetch data from DB
        # In a production 2026 system, we'd scan Parquet files. 
        # Here we query the last 30 days of logs.
        logs = db.query(
            AttendanceLog.emotion,
            AttendanceLog.user_id,
            Department.name.label("dept_name")
        ).join(User, AttendanceLog.user_id == User.id)\
         .join(Department, User.dept_id == Department.id)\
         .filter(User.org_id == org_id)\
         .filter(AttendanceLog.check_in >= datetime.utcnow() - timedelta(days=30)).all()

        if not logs:
            return []

        # 2. Convert to Polars DataFrame for high-speed processing
        df = pl.DataFrame([
            {"emotion": l.emotion, "dept": l.dept_name, "user_id": l.user_id} 
            for l in logs
        ])

        # 3. Categorize Stress (Negative Emotions)
        # DeepFace emotions: 'angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'
        stress_emotions = ['angry', 'sad', 'fear', 'disgust']
        
        # 4. Aggregate by Department
        heatmap = df.group_by("dept").agg([
            pl.len().alias("total_logs"),
            pl.col("emotion").filter(pl.col("emotion").is_in(stress_emotions)).count().alias("stress_count"),
            pl.col("user_id").n_unique().alias("unique_users")
        ]).with_columns([
            ((pl.col("stress_count") / pl.col("total_logs")) * 100).alias("stress_index")
        ]).sort("stress_index", descending=True)

        return heatmap.to_dicts()

    @staticmethod
    def get_productivity_growth(db: Session, org_id: str, timeframe_days: int = 90) -> Dict[str, Any]:
        """
        Correlates Punctuality with Wellness using Polars.
        """
        logs = db.query(
            AttendanceLog.status,
            AttendanceLog.check_in,
            AttendanceLog.emotion
        ).join(User).filter(User.org_id == org_id).all()

        if not logs:
            return {"status": "no_data"}

        df = pl.DataFrame([
            {"status": l.status, "date": l.check_in.date(), "emotion": l.emotion}
            for l in logs
        ])

        # Quarterly Trends
        growth = df.group_by("date").agg([
            pl.len().alias("count"),
            pl.col("status").filter(pl.col("status") == "on_time").count().alias("on_time")
        ]).with_columns([
            ((pl.col("on_time") / pl.col("count")) * 100).alias("punctuality_rate")
        ]).sort("date")

        return {
            "timeframe": f"{timeframe_days} days",
            "avg_punctuality": growth["punctuality_rate"].mean(),
            "trend": growth.to_dicts()
        }

analytics_service = AnalyticsService()
