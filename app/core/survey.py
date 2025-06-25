from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import DestinationTag, Destination, Tag

# 1) 설문 문항 → 태그 raw 매핑 (0/1)
QUESTION_TAG_MAP: Dict[str, Dict[str, Dict[str, int]]] = {
    "q1": {"A": {"sightseeing": 1}, "B": {"relaxation": 1}},
    "q2": {"A": {"beach": 1},       "B": {"mountain": 1}},
    "q3": {
        "A": {"solo": 1},   "B": {"friends": 1},
        "C": {"family": 1}, "D": {"couple": 1}
    },
    "q4": {"A": {"warm": 1}, "B": {"comfortable": 1}, "C": {"cool": 1}, "D": {"cold": 1}},
    "q5": {"A": {"traditional": 1}, "B": {"fusion": 1}, "C": {"street": 1},  "D": {"vegan": 1}},
    "q6": {"A": {"car": 1},      "B": {"public": 1},     "C": {"walk": 1},    "D": {"bus": 1}},
    "q7": {"A": {"leisure": 1},  "B": {"normal": 1},     "C": {"tight": 1},   "D": {"spontaneous": 1}},
}

# 2) 문항별 가중치
QUESTION_WEIGHTS: Dict[str, int] = {
    "q1": 3,
    "q2": 2,
    **{f"q{i}": 1 for i in range(3, 8)}
}


def build_profile(answers: Dict[str, str]) -> Dict[str, int]:
    """
    설문 응답(answers)으로부터 사용자 태그 가중치 프로필 반환
    :param answers: { "q1": "A", ..., "q7": "D" }
    :return: { "beach": weight, "sightseeing": weight, ... }
    """
    profile: Dict[str, int] = {}
    for q_key, choice in answers.items():
        tag_map = QUESTION_TAG_MAP.get(q_key, {})
        tags = tag_map.get(choice, {})
        weight = QUESTION_WEIGHTS.get(q_key, 1)
        for tag_name, raw_val in tags.items():
            profile[tag_name] = profile.get(tag_name, 0) + raw_val * weight
    return profile


def run_recommendation(profile: Dict[str, int], db: Session, top_n: int = 3) -> List[Dict[str, int]]:
    """
    사용자 프로필을 바탕으로 DB에서 destination_tag.score 가져와 내적 계산 후 상위 top_n 추천
    :param profile: 사용자 { tag_name: weight }
    :param db: SQLAlchemy Session
    :param top_n: 추천 개수
    :return: [ { "name": str, "score": int }, ... ]
    """
    # 1) 관심 있는 태그 ID 목록 조회
    tag_names = list(profile.keys())
    tag_rows = db.execute(select(Tag.id, Tag.name).where(Tag.name.in_(tag_names))).all()
    tagid_to_name = {row.id: row.name for row in tag_rows}
    tag_ids = list(tagid_to_name.keys())

    if not tag_ids:
        return []

    # 2) destination_tag에서 raw_score 조회 (모델에 score 컬럼 사용)
    rows = db.execute(
        select(
            DestinationTag.destination_id,
            DestinationTag.score,
            DestinationTag.tag_id
        ).where(DestinationTag.tag_id.in_(tag_ids))
    ).all()

    # 3) 내적 계산: destination_id 별 누적 점수
    scores: Dict[int, int] = {}
    for dest_id, raw_score, tag_id in rows:
        tag_name = tagid_to_name.get(tag_id)
        user_weight = profile.get(tag_name, 0)
        scores[dest_id] = scores.get(dest_id, 0) + raw_score * user_weight

    # 4) 상위 top_n dest_id 추출
    top_dest = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # 5) destination 이름 조회 및 결과 포맷
    recommendations: List[Dict[str, int]] = []
    for dest_id, total_score in top_dest:
        dest = db.get(Destination, dest_id)
        if dest:
            recommendations.append({
                "name": dest.name,
                "description": dest.description,
                "country" : dest.country,
                "latitude" : dest.latitude,                
                "longitude" : dest.longitude,
                "score": total_score
            })
    return recommendations
