# /fortify_web_analyzer/app/analysis_logic.py

from app import db
from app.models import RulePack, Rule

def run_analysis(pack_ids_to_compare):
    """
    비교할 RulePack의 ID 목록(2개로 가정)을 받아 분석을 수행하고,
    결과를 구조화된 딕셔너리로 반환합니다.
    """
    if len(pack_ids_to_compare) != 2:
        return {"error": "비교를 위해 정확히 2개의 룰팩을 선택해야 합니다."}

    pack_id_a, pack_id_b = pack_ids_to_compare

    # 1. DB에서 선택된 두 룰팩의 정보를 가져옵니다.
    pack_a = RulePack.query.get(pack_id_a)
    pack_b = RulePack.query.get(pack_id_b)

    if not pack_a or not pack_b:
        return {"error": "선택된 룰팩 정보를 DB에서 찾을 수 없습니다."}

    # 2. 각 룰팩에 속한 모든 규칙의 '이름'만 가져와서 세트(set)로 만듭니다.
    # 세트를 사용하면 교집합, 차집합 연산이 매우 빠릅니다.
    rules_a_set = {rule.rule_name for rule in pack_a.rules}
    rules_b_set = {rule.rule_name for rule in pack_b.rules}

    # 3. 세트 연산을 통해 규칙들을 비교합니다.
    common_rules = sorted(list(rules_a_set.intersection(rules_b_set)))
    only_in_a = sorted(list(rules_a_set.difference(rules_b_set)))
    only_in_b = sorted(list(rules_b_set.difference(rules_a_set)))

    # 4. 최종 결과를 보기 좋은 딕셔너리 형태로 정리하여 반환합니다.
    results_data = {
        "pack_a": {
            "name": pack_a.pack_name,
            "version": pack_a.pack_version,
            "location": pack_a.location,
            "total_rules": len(rules_a_set)
        },
        "pack_b": {
            "name": pack_b.pack_name,
            "version": pack_b.pack_version,
            "location": pack_b.location,
            "total_rules": len(rules_b_set)
        },
        "comparison": {
            "common_rules": common_rules,
            "only_in_a": only_in_a,
            "only_in_b": only_in_b
        }
    }

    return results_data