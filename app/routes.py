import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Rule, ExternalMapping, RulePack, Log
import xml.etree.ElementTree as ET
from app.analysis_logic import run_analysis

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    # 사용자가 목록에서 특정 규칙을 클릭했을 때 (GET 요청)
    rule_id = request.args.get('rule_id', type=int)
    if rule_id:
        selected_rule = Rule.query.get_or_404(rule_id)
        return render_template('index.html',
                               selected_rule=selected_rule,
                               mappings=selected_rule.mappings)

    # 사용자가 검색어를 입력하고 폼을 제출했을 때 (POST 요청)
    if request.method == 'POST':
        rule_name_from_form = request.form.get('rule_name', '').strip()
        
        # 로그 기록 (상태: Search)
        current_app.logger.info(f"룰 검색 실행: '{rule_name_from_form}'", extra={'status': 'Search'})
        
        if not rule_name_from_form:
            flash('오류: 검색할 규칙 이름을 입력해주세요.', 'error')
            return render_template('index.html')

        search_term = f"%{rule_name_from_form}%"
        found_rules = Rule.query.filter(Rule.rule_name.like(search_term)).order_by(Rule.rule_name).all()
        
        return render_template('index.html',
                               searched_term=rule_name_from_form,
                               found_rules=found_rules)
    
    # 그냥 메인 페이지에 처음 접속했을 때 (GET 요청)
    return render_template('index.html')


@bp.route('/upload', methods=['GET', 'POST'])
def upload_and_parse():
    if request.method == 'POST':
        log_extra = {'status': 'Upload'}
        current_app.logger.info("파일 업로드 요청을 받았습니다.", extra=log_extra)
        uploaded_files = request.files.getlist('xml_files')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('오류: 분석할 폴더를 선택해주세요.', 'error')
            current_app.logger.warning("업로드된 파일이 없습니다. 요청이 중단되었습니다.", extra=log_extra)
            return redirect(request.url)

        try:
            processed_files_count = 0
            for file in uploaded_files:
                if file and file.filename.endswith('externalmetadata.xml'):
                    location = file.filename
                    current_app.logger.info(f"'{location}' 파일 처리 시작...")

                    # --- ✨ 로직 변경: 파일 경로(location)로 DB에 이미 있는지 확인 ---
                    existing_pack = RulePack.query.filter_by(location=location).first()
                    if existing_pack:
                        message = f"경고: '{location}' 파일은 이미 DB에 존재하므로 건너뜁니다."
                        flash(message, 'warning')
                        current_app.logger.warning(message, extra=log_extra)
                        continue # 다음 파일로 넘어감

                    # --- DB에 없는 새로운 파일이면 처리 시작 ---
                    processed_files_count += 1
                    try:
                        xml_content = file.read().decode('utf-8')
                        root = ET.fromstring(xml_content)
                        namespace = {'ns': root.tag.split('}')[0][1:]}

                        pack_info_element = root.find('ns:PackInfo', namespace)
                        if pack_info_element is None:
                            message = f"경고: 파일 '{location}'에서 <PackInfo>를 찾을 수 없어 건너뜁니다."
                            flash(message, 'error')
                            current_app.logger.warning(message, extra=log_extra)
                            continue
                        
                        pack_name = pack_info_element.find('ns:Name', namespace).text
                        pack_id = pack_info_element.find('ns:PackID', namespace).text
                        pack_version = pack_info_element.find('ns:Version', namespace).text

                        # 새로운 룰팩 객체 생성 (location 포함)
                        new_rule_pack = RulePack(pack_name=pack_name, pack_id=pack_id, pack_version=pack_version, location=location)
                        db.session.add(new_rule_pack)
                        
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
                                    # Rule 생성 시, 새로 만든 new_rule_pack과 연결
                                    current_rule = Rule(rule_name=rule_name, rule_pack=new_rule_pack)
                                    db.session.add(current_rule)
                                    rule_cache[rule_name] = current_rule

                                new_mapping = ExternalMapping(standard_info=standard_info, rule=current_rule)
                                db.session.add(new_mapping)
                                added_mappings.add((rule_name, standard_info))
                        
                        # 각 파일 처리가 성공하면 DB에 커밋
                        db.session.commit()
                        message = f"✅ (처리 완료) '{location}' 파일의 룰팩과 규칙들을 DB에 새로 추가했습니다."
                        flash(message, 'success')
                        current_app.logger.info(message, extra=log_extra)

                    except Exception as e:
                        db.session.rollback()
                        flash(f"오류: 파일 '{location}' 처리 중 문제가 발생했습니다. (로그 확인 필요)", 'error')
                        current_app.logger.error(f"'{location}' 파일 처리 중 오류 발생.", exc_info=True, extra=log_extra)
            
            if processed_files_count == 0 and len(uploaded_files) > 0:
                 flash('선택한 폴더에 처리할 새로운 `externalmetadata.xml` 파일이 없습니다.', 'info')

        except Exception as e:
            flash(f'전체 업로드 과정에서 예기치 못한 오류 발생: {e}', 'error')
            current_app.logger.error("업로드 처리 중 예기치 못한 오류 발생.", exc_info=True, extra=log_extra)
        
        return redirect(url_for('main.upload_and_parse'))
        
    return render_template('upload.html')


@bp.route('/analyzer', methods=['GET', 'POST'])
def analyzer():
    # POST 요청: 사용자가 룰팩을 선택하고 '비교 분석'을 눌렀을 때
    if request.method == 'POST':
        pack_ids_to_compare = request.form.getlist('packs_to_compare')
        
        if len(pack_ids_to_compare) < 2:
            flash('오류: 비교하려면 룰팩을 2개 이상 선택해야 합니다.', 'error')
            return redirect(url_for('main.analyzer'))

        # 로그 기록 (상태: Analyzer)
        current_app.logger.info(f"룰팩 비교 분석 실행. 대상 ID: {pack_ids_to_compare}", extra={'status': 'Analyzer'})
        
        analysis_results = run_analysis(pack_ids_to_compare)
        all_packs = RulePack.query.order_by(RulePack.pack_version.desc()).all()
        return render_template('analyzer.html', 
                               rule_packs=all_packs, 
                               results=analysis_results)

    # GET 요청: 그냥 /analyzer 페이지에 접속했을 때
    all_packs = RulePack.query.order_by(RulePack.pack_version.desc()).all()
    return render_template('analyzer.html', rule_packs=all_packs)


@bp.route('/logs')
def view_logs():
    # 로그 기록 (상태: System)
    current_app.logger.info("로그 보기 페이지에 접근했습니다.", extra={'status': 'System'})
    # DB에서 모든 로그를 가져오되, 최신순으로 정렬하여 100개만 가져옵니다.
    logs = Log.query.order_by(Log.timestamp.desc()).limit(100).all()
    return render_template('logs.html', logs=logs)