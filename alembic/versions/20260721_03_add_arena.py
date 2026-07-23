"""add bug bounty arena"""

from alembic import op
import sqlalchemy as sa

revision = "20260721_03"
down_revision = "20260706_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False, unique=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("target_path", sa.String(length=255), nullable=False),
        sa.Column("brief", sa.Text(), nullable=False),
        sa.Column("bounty_note", sa.Text(), nullable=False),
        sa.Column("flag", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_challenges_slug", "challenges", ["slug"])
    op.create_index("ix_challenges_category", "challenges", ["category"])
    op.create_table(
        "challenge_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("challenges.id"), nullable=False),
        sa.Column("submitted_flag", sa.String(length=120), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge_submission"),
    )
    op.create_index("ix_challenge_submissions_user_id", "challenge_submissions", ["user_id"])
    op.create_index(
        "ix_challenge_submissions_challenge_id",
        "challenge_submissions",
        ["challenge_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_challenge_submissions_challenge_id", table_name="challenge_submissions")
    op.drop_index("ix_challenge_submissions_user_id", table_name="challenge_submissions")
    op.drop_table("challenge_submissions")
    op.drop_index("ix_challenges_category", table_name="challenges")
    op.drop_index("ix_challenges_slug", table_name="challenges")
    op.drop_table("challenges")
