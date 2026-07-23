from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.auth import get_current_user
from app.core.database import get_db
from app.models.challenge import Challenge, ChallengeSubmission
from app.models.user import User

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(prefix="/arena")


@router.get("")
def arena_home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    challenges = db.scalars(select(Challenge).order_by(Challenge.category, Challenge.points)).all()
    solved_ids: set[int] = set()
    if user:
        solved_ids = set(
            db.scalars(
                select(ChallengeSubmission.challenge_id).where(
                    ChallengeSubmission.user_id == user.id
                )
            ).all()
        )

    categories = sorted({challenge.category for challenge in challenges})
    return templates.TemplateResponse(
        request,
        "arena.html",
        {
            "user": user,
            "challenges": challenges,
            "categories": categories,
            "solved_ids": solved_ids,
        },
    )


@router.get("/scoreboard")
def scoreboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    scores = db.execute(
        select(
            User.id,
            User.nickname,
            User.username,
            func.coalesce(func.sum(ChallengeSubmission.points_awarded), 0).label("score"),
            func.count(ChallengeSubmission.id).label("solves"),
            func.max(ChallengeSubmission.created_at).label("last_solve"),
        )
        .outerjoin(ChallengeSubmission, ChallengeSubmission.user_id == User.id)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(ChallengeSubmission.points_awarded), 0).desc())
    ).all()
    return templates.TemplateResponse(
        request,
        "scoreboard.html",
        {"user": user, "scores": scores},
    )


@router.post("/submit")
def submit_flag(
    request: Request,
    challenge_id: int = Form(...),
    flag: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    challenge = db.get(Challenge, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")

    normalized_flag = flag.strip()
    if normalized_flag != challenge.flag:
        return RedirectResponse(url="/arena?error=invalid", status_code=303)

    submission = ChallengeSubmission(
        user_id=user.id,
        challenge_id=challenge.id,
        submitted_flag=normalized_flag,
        points_awarded=challenge.points,
    )
    db.add(submission)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse(url="/arena?status=already", status_code=303)

    return RedirectResponse(url="/arena/scoreboard", status_code=303)
