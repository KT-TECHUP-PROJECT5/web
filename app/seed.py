from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.challenge import Challenge
from app.models.post import Post
from app.models.user import User


CHALLENGES = [
    {
        "slug": "a01-private-idor",
        "title": "비공개 게시글 IDOR",
        "category": "A01 Broken Access Control",
        "difficulty": "easy",
        "points": 100,
        "target_path": "/posts/private/2",
        "brief": "다른 사용자의 비공개 게시글을 직접 객체 참조로 열람합니다.",
        "bounty_note": "힌트: user2의 비공개 글 번호를 추측해 보세요.",
        "flag": "flag{idor_private_post}",
    },
    {
        "slug": "a01-admin-bypass",
        "title": "관리자 페이지 접근제어 미흡",
        "category": "A01 Broken Access Control",
        "difficulty": "medium",
        "points": 180,
        "target_path": "/admin",
        "brief": "일반 사용자 세션으로 운영 관리 화면 접근 가능성을 검증합니다.",
        "bounty_note": "힌트: 권한 확인이 화면 링크에만 의존하는지 살펴보세요.",
        "flag": "flag{admin_gate_open}",
    },
    {
        "slug": "a02-dangerous-upload",
        "title": "무제한 파일 업로드",
        "category": "A02 Security Misconfiguration",
        "difficulty": "easy",
        "points": 120,
        "target_path": "/upload",
        "brief": "확장자, MIME, 크기 제한 없이 위험 파일이 저장되는지 확인합니다.",
        "bounty_note": "힌트: HTML, SVG, PHP처럼 서버가 받아들이면 곤란한 파일을 시도하세요.",
        "flag": "flag{upload_without_guardrails}",
    },
    {
        "slug": "a03-legacy-deps",
        "title": "취약 의존성 흔적",
        "category": "A03 Supply Chain",
        "difficulty": "easy",
        "points": 100,
        "target_path": "/cve",
        "brief": "구버전 의존성 파일을 기준으로 알려진 취약 패키지를 식별합니다.",
        "bounty_note": "힌트: requirements-legacy.txt가 별도 실습 표적입니다.",
        "flag": "flag{legacy_dependencies}",
    },
    {
        "slug": "a05-login-sqli",
        "title": "로그인 SQL Injection",
        "category": "A05 Injection",
        "difficulty": "medium",
        "points": 200,
        "target_path": "/login",
        "brief": "문자열 조합 SQL을 우회해 인증을 통과합니다.",
        "bounty_note": "힌트: 고전적인 OR 조건과 주석 처리를 떠올려 보세요.",
        "flag": "flag{sqli_login_bypass}",
    },
    {
        "slug": "a05-reflected-xss",
        "title": "검색어 Reflected XSS",
        "category": "A05 Injection",
        "difficulty": "easy",
        "points": 120,
        "target_path": "/posts?keyword=",
        "brief": "검색 결과 화면에 사용자 입력이 그대로 반사되는지 검증합니다.",
        "bounty_note": "힌트: 검색어 출력 위치를 확인하세요.",
        "flag": "flag{reflected_search_xss}",
    },
    {
        "slug": "a07-weak-password",
        "title": "약한 비밀번호 허용",
        "category": "A07 Authentication Failures",
        "difficulty": "easy",
        "points": 90,
        "target_path": "/register",
        "brief": "짧고 단순한 비밀번호로 신규 계정을 만들 수 있는지 확인합니다.",
        "bounty_note": "힌트: 1234 같은 값도 거절되는지 보세요.",
        "flag": "flag{weak_password_allowed}",
    },
    {
        "slug": "a09-no-security-events",
        "title": "보안 이벤트 미기록",
        "category": "A09 Logging Failures",
        "difficulty": "medium",
        "points": 160,
        "target_path": "/admin/security-events",
        "brief": "공격성 요청 이후에도 감사 로그가 비어 있는지 확인합니다.",
        "bounty_note": "힌트: 공격을 하나 수행한 뒤 기록 화면을 확인하세요.",
        "flag": "flag{silent_attacks}",
    },
    {
        "slug": "a10-debug-leak",
        "title": "디버그 오류 정보 노출",
        "category": "A10 Exceptional Conditions",
        "difficulty": "easy",
        "points": 110,
        "target_path": "/debug/error",
        "brief": "예외 메시지와 내부 구현 정보가 사용자에게 노출되는지 확인합니다.",
        "bounty_note": "힌트: debug 경로 3종을 비교하세요.",
        "flag": "flag{debug_error_leak}",
    },
    {
        "slug": "bonus-delete-any-post",
        "title": "타인 게시글 삭제",
        "category": "Bonus Bug Bounty",
        "difficulty": "hard",
        "points": 260,
        "target_path": "/posts/{post_id}/delete",
        "brief": "작성자 검증 없는 삭제 엔드포인트로 영향 범위를 증명합니다.",
        "bounty_note": "힌트: 관리자 화면에서 호출되는 POST 요청을 관찰하세요.",
        "flag": "flag{delete_without_owner_check}",
    },
]


def seed_database() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User.id).limit(1)) is None:
            admin = User(username="admin", password="admin123", nickname="관리자", role="admin")
            user1 = User(username="user1", password="password123", nickname="사용자1")
            user2 = User(username="user2", password="password123", nickname="사용자2")
            db.add_all([admin, user1, user2])
            db.flush()

            db.add_all(
                [
                    Post(user_id=user1.id, title="user1 공개 게시글", content="공개 글입니다."),
                    Post(
                        user_id=user1.id,
                        title="user1 비공개 게시글",
                        content="IDOR 확인용 비공개 글입니다.",
                        is_private=True,
                    ),
                    Post(user_id=user2.id, title="user2 공개 게시글", content="공개 글입니다."),
                    Post(
                        user_id=user2.id,
                        title="user2 비공개 게시글",
                        content="다른 계정에서 직접 접근해 보세요.\nflag{idor_private_post}",
                        is_private=True,
                    ),
                ]
            )

        existing_slugs = set(db.scalars(select(Challenge.slug)).all())
        db.add_all(
            [
                Challenge(**challenge)
                for challenge in CHALLENGES
                if challenge["slug"] not in existing_slugs
            ]
        )
        user2_private_post = db.scalar(
            select(Post).where(Post.title == "user2 비공개 게시글").limit(1)
        )
        if user2_private_post and "flag{idor_private_post}" not in user2_private_post.content:
            user2_private_post.content = (
                f"{user2_private_post.content}\nflag{{idor_private_post}}"
            )
        db.commit()
        print("seed complete")


if __name__ == "__main__":
    seed_database()
