# /fortify_web_analyzer/app/analysis_logic.py

from app import db
from app.models import RulePack, Rule, ExternalMapping
import xml.etree.ElementTree as ET

def process_uploaded_rulepack_files(files):
    """
    업로드된 파일 목록을 받아 파싱하고 DB에 저장하는 모든 로직을 처리합니다.
    처리 결과 메시지 리스트를 반환합니다.
    """
    messages = []
    
    for file in files:
        # 파일 이름이 'externalmetadata.xml'로 끝나는 경우에만 처리합니다.
        if file and file.filename.endswith('externalmetadata.xml'):
            location = file.filename
            
            # DB에 동일한 경로의 파일이 이미 있는지 확인합니다.
            existing_pack = RulePack.query.filter_by(location=location).first()
            if existing_pack:
                messages.append({'category': 'warning', 'text': f"경고: '{location}' 파일은 이미 DB에 존재하므로 건너뜁니다."})
                continue

            try:
                # 파일 포인터를 처음으로 되돌려 파일 내용을 읽습니다.
                file.seek(0)
                xml_content = file.read().decode('utf-8')
                root = ET.fromstring(xml_content)
                namespace = {'ns': root.tag.split('}')[0][1:]}

                # PackInfo 파싱
                pack_info_element = root.find('ns:PackInfo', namespace)
                if pack_info_element is None:
                    messages.append({'category': 'error', 'text': f"경고: 파일 '{location}'에서 <PackInfo>를 찾을 수 없어 건너뜁니다."})
                    continue
                
                pack_name = pack_info_element.find('ns:Name', namespace).text
                pack_id = pack_info_element.find('ns:PackID', namespace).text
                pack_version = pack_info_element.find('ns:Version', namespace).text

                # 새로운 RulePack 객체 생성
                new_rule_pack = RulePack(pack_name=pack_name, pack_id=pack_id, pack_version=pack_version, location=location)
                db.session.add(new_rule_pack)
                
                # 규칙 및 매핑 정보 파싱 및 저장
                rule_cache = {}
                added_mappings = set()
                for mapping in root.findall('.//ns:Mapping', namespace):
                    internal_cat = mapping.find('ns:InternalCategory', namespace)
                    external_cat = mapping.find('ns:ExternalCategory', namespace)

                    if internal_cat is not None and external_cat is not None:
                        rule_name = internal_cat.text
                        standard_info = external_cat.text
                        
                        if (rule_name, standard_info) in added_mappings:
                            continue
                        
                        current_rule = rule_cache.get(rule_name)
                        if not current_rule:
                            current_rule = Rule(rule_name=rule_name, rule_pack=new_rule_pack)
                            db.session.add(current_rule)
                            rule_cache[rule_name] = current_rule

                        new_mapping = ExternalMapping(standard_info=standard_info, rule=current_rule)
                        db.session.add(new_mapping)
                        added_mappings.add((rule_name, standard_info))
                
                # 각 파일 처리가 성공하면 DB에 커밋
                db.session.commit()
                messages.append({'category': 'success', 'text': f"✅ (처리 완료) '{location}' 파일의 룰팩과 규칙들을 DB에 새로 추가했습니다."})
            except Exception as e:
                db.session.rollback()
                messages.append({'category': 'error', 'text': f"오류: 파일 '{location}' 처리 중 문제가 발생했습니다. ({e})"})
    
    return messages

def run_analysis(pack_ids_to_compare):
    """
    비교할 RulePack의 ID 목록(2개로 가정)을 받아 분석을 수행하고,
    결과를 구조화된 딕셔너리로 반환합니다.
    """
    if len(pack_ids_to_compare) < 2:
        return {"error": "비교를 위해 2개 이상의 룰팩을 선택해야 합니다."}

    pack_objects = RulePack.query.filter(RulePack.id.in_(pack_ids_to_compare)).all()

    if len(pack_objects) < 2:
        return {"error": "선택된 룰팩 정보를 DB에서 찾을 수 없습니다."}
    
    pack_a = pack_objects[0]
    pack_b = pack_objects[1]
    
    rules_a_set = {rule.rule_name for rule in pack_a.rules}
    rules_b_set = {rule.rule_name for rule in pack_b.rules}

    common_rules = sorted(list(rules_a_set.intersection(rules_b_set)))
    only_in_a = sorted(list(rules_a_set.difference(rules_b_set)))
    only_in_b = sorted(list(rules_b_set.difference(rules_a_set)))

    results_data = {
        "pack_a": { "name": pack_a.pack_name, "version": pack_a.pack_version, "location": pack_a.location, "total_rules": len(rules_a_set) },
        "pack_b": { "name": pack_b.pack_name, "version": pack_b.pack_version, "location": pack_b.location, "total_rules": len(rules_b_set) },
        "comparison": { "common_rules": common_rules, "only_in_a": only_in_a, "only_in_b": only_in_b }
    }
    return results_data