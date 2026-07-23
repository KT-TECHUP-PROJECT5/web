from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), index=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="easy")
    points: Mapped[int] = mapped_column(Integer, default=100)
    target_path: Mapped[str] = mapped_column(String(255))
    brief: Mapped[str] = mapped_column(Text)
    bounty_note: Mapped[str] = mapped_column(Text)
    flag: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submissions: Mapped[list["ChallengeSubmission"]] = relationship(  # noqa: F821
        back_populates="challenge"
    )


class ChallengeSubmission(Base):
    __tablename__ = "challenge_submissions"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge_submission"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), index=True)
    submitted_flag: Mapped[str] = mapped_column(String(120))
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="challenge_submissions")  # noqa: F821
    challenge: Mapped[Challenge] = relationship(back_populates="submissions")
