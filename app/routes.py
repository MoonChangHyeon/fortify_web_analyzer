# /fortify_web_analyzer/app/routes.py

import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app import db
# ✨ 수정: Rule과 ExternalMapping을 함께 가져옵니다.
from app.models import Rule, ExternalMapping, RulePack
import xml.etree.ElementTree as ET
from app.analysis_logic import run_analysis

bp = Blueprint('main', __name__)

# --- index 함수 (변경 없음) ---
@bp.route('/', methods=['GET', 'POST'])
def index():
    rule_id = request.args.get('rule_id', type=int)
    if rule_id:
        selected_rule = Rule.query.get_or_404(rule_id)
        return render_template('index.html',
                               selected_rule=selected_rule,
                               mappings=selected_rule.mappings)

    if request.method == 'POST':
        rule_name_from_form = request.form.get('rule_name', '').strip()
        
        if not rule_name_from_form:
            flash('오류: 검색할 규칙 이름을 입력해주세요.', 'error')
            return render_template('index.html')

        search_term = f"%{rule_name_from_form}%"
        found_rules = Rule.query.filter(Rule.rule_name.like(search_term)).order_by(Rule.rule_name).all()
        
        return render_template('index.html',
                               searched_term=rule_name_from_form,
                               found_rules=found_rules)
    
    return render_template('index.html')


# --- upload_and_parse 함수 (수정됨) ---
@bp.route('/upload', methods=['GET', 'POST'])
def upload_and_parse():
    if request.method == 'POST':
        # 1. 여러 파일을 리스트로 받습니다.
        uploaded_files = request.files.getlist('xml_files')
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('오류: 업로드할 파일을 선택해주세요.', 'error')
            return redirect(request.url)

        try:
            # 여러 파일에서 추가된 룰과 매핑의 총 개수를 셉니다.
            total_rules_created = 0
            total_mappings_created = 0

            # 2. 업로드된 각 파일을 순서대로 처리합니다.
            for file in uploaded_files:
                if file and file.filename.endswith('.xml'):
                    xml_content = file.read().decode('utf-8')
                    root = ET.fromstring(xml_content)
                    namespace = {'ns': root.tag.split('}')[0][1:]}

                    # 3. 파일에서 <PackInfo>를 파싱합니다.
                    pack_info_element = root.find('ns:PackInfo', namespace)
                    if pack_info_element is None:
                        flash(f"경고: 파일 '{file.filename}'에서 <PackInfo>를 찾을 수 없어 건너뜁니다.", 'error')
                        continue
                    
                    pack_name = pack_info_element.find('ns:Name', namespace).text
                    pack_id = pack_info_element.find('ns:PackID', namespace).text
                    pack_version = pack_info_element.find('ns:Version', namespace).text

                    # 4. DB에서 PackID로 기존 룰팩이 있는지 확인하고, 없으면 새로 만듭니다.
                    rule_pack = RulePack.query.filter_by(pack_id=pack_id).first()
                    if not rule_pack:
                        rule_pack = RulePack(pack_name=pack_name, pack_id=pack_id, pack_version=pack_version)
                        db.session.add(rule_pack)
                        flash(f"새로운 룰팩 '{pack_name} ({pack_version})'을 DB에 추가합니다.", 'info')
                    else:
                        # 기존 룰팩 정보가 있다면, 관련 규칙들을 모두 삭제하여 업데이트를 준비합니다.
                        flash(f"기존 룰팩 '{pack_name} ({pack_version})'의 데이터를 업데이트합니다.", 'info')
                        Rule.query.filter_by(rule_pack_id=rule_pack.id).delete()

                    db.session.commit() # 룰팩을 먼저 DB에 반영하여 ID를 확정합니다.

                    # 5. 규칙(Rule) 및 매핑(ExternalMapping) 정보를 파싱하여 DB에 저장합니다.
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
                            
                            # 규칙을 DB에서 찾거나 새로 생성 (이때 rule_pack과 연결!)
                            current_rule = rule_cache.get(rule_name)
                            if not current_rule:
                                current_rule = Rule(rule_name=rule_name, rule_pack=rule_pack)
                                db.session.add(current_rule)
                                rule_cache[rule_name] = current_rule
                                total_rules_created += 1

                            new_mapping = ExternalMapping(standard_info=standard_info, rule=current_rule)
                            db.session.add(new_mapping)
                            added_mappings.add((rule_name, standard_info))
                    
                    total_mappings_created += len(added_mappings)

            # 6. 모든 파일 처리가 끝난 후, DB에 최종 저장합니다.
            db.session.commit()
            flash(f'성공: 총 {total_rules_created}개의 룰과 {total_mappings_created}개의 매핑 정보를 DB에 저장했습니다.', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'파싱 중 오류 발생: {e}', 'error')
        
        return redirect(url_for('main.upload_and_parse'))
        
    return render_template('upload.html')

@bp.route('/analyzer', methods=['GET', 'POST'])
def analyzer():
    # POST 요청: 사용자가 룰팩을 선택하고 '비교 분석'을 눌렀을 때
    if request.method == 'POST':
        # 체크박스에서 선택된 pack_id들을 리스트로 받습니다.
        pack_ids_to_compare = request.form.getlist('packs_to_compare')
        
        if len(pack_ids_to_compare) < 2:
            flash('오류: 비교하려면 룰팩을 2개 이상 선택해야 합니다.', 'error')
            return redirect(url_for('main.analyzer'))

        # 분석 로직 함수에 pack_id 리스트를 전달하고 결과를 받습니다.
        analysis_results = run_analysis(pack_ids_to_compare)

        # 모든 룰팩 목록을 다시 가져와서 화면에 표시합니다.
        all_packs = RulePack.query.order_by(RulePack.pack_version.desc()).all()
        return render_template('analyzer.html', 
                               rule_packs=all_packs, 
                               results=analysis_results)

    # GET 요청: 그냥 /analyzer 페이지에 접속했을 때
    # DB에 있는 모든 룰팩 목록을 가져와서 화면에 뿌려줍니다.
    all_packs = RulePack.query.order_by(RulePack.pack_version.desc()).all()
    return render_template('analyzer.html', rule_packs=all_packs)

# ✨ 수정: 맨 아래에 있던 불필요한 import 구문을 삭제했습니다.