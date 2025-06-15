# /fortify_web_analyzer/app/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app.models import Rule, RulePack, Log
from app.analysis_logic import run_analysis, process_uploaded_rulepack_files

bp = Blueprint('main', __name__)

@bp.route('/upload', methods=['GET', 'POST'])
def upload_and_parse():
    if request.method == 'POST':
        log_extra = {'status': 'Upload'}
        current_app.logger.info("파일 업로드 요청을 받았습니다.", extra=log_extra)
        uploaded_files = request.files.getlist('xml_files')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('오류: 분석할 폴더를 선택해주세요.', 'error')
            current_app.logger.warning("업로드된 파일이 없습니다.", extra=log_extra)
            return redirect(request.url)
        
        # ✨ 실제 처리는 analysis_logic.py의 함수에 모두 위임합니다 ✨
        messages = process_uploaded_rulepack_files(uploaded_files)

        # 처리 결과 메시지를 화면과 로그에 기록합니다.
        processed_count = 0
        for msg in messages:
            flash(msg['text'], msg['category'])
            if msg['category'] == 'success':
                processed_count += 1
            
            if msg['category'] == 'error':
                 current_app.logger.error(msg['text'], extra=log_extra)
            else:
                 current_app.logger.info(msg['text'], extra=log_extra)
        
        if processed_count == 0 and not any(m['category'] == 'warning' for m in messages):
             flash('선택한 폴더에서 처리할 새로운 `externalmetadata.xml` 파일이 없습니다.', 'info')
        
        current_app.logger.info(f"업로드 처리 완료. 총 {processed_count}개 신규 파일 처리됨.", extra=log_extra)
        
        return redirect(url_for('main.upload_and_parse'))
        
    return render_template('upload.html')

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        rule_name_from_form = request.form.get('rule_name', '').strip()
        current_app.logger.info(f"룰 검색 실행: '{rule_name_from_form}'", extra={'status': 'Search'})
        
        if not rule_name_from_form:
            flash('오류: 검색할 규칙 이름을 입력해주세요.', 'error')
            return render_template('index.html')

        search_term = f"%{rule_name_from_form}%"
        found_rules = Rule.query.filter(Rule.rule_name.like(search_term)).order_by(Rule.rule_name).all()
        
        return render_template('index.html',
                               searched_term=rule_name_from_form,
                               found_rules=found_rules)
    
    rule_id = request.args.get('rule_id', type=int)
    if rule_id:
        selected_rule = Rule.query.get_or_404(rule_id)
        return render_template('index.html',
                               selected_rule=selected_rule,
                               mappings=selected_rule.mappings)
    
    return render_template('index.html')


@bp.route('/analyzer', methods=['GET', 'POST'])
def analyzer():
    if request.method == 'POST':
        pack_ids_to_compare = request.form.getlist('packs_to_compare')
        
        if len(pack_ids_to_compare) < 2:
            flash('오류: 비교하려면 룰팩을 2개 이상 선택해야 합니다.', 'error')
            return redirect(url_for('main.analyzer'))

        current_app.logger.info(f"룰팩 비교 분석 실행. 대상 ID: {pack_ids_to_compare}", extra={'status': 'Analyzer'})
        analysis_results = run_analysis(pack_ids_to_compare)
        
        all_packs = RulePack.query.order_by(RulePack.pack_version.desc()).all()
        return render_template('analyzer.html', 
                               rule_packs=all_packs, 
                               results=analysis_results)

    all_packs = RulePack.query.order_by(RulePack.pack_version.desc()).all()
    return render_template('analyzer.html', rule_packs=all_packs)


@bp.route('/logs')
def view_logs():
    current_app.logger.info("로그 보기 페이지에 접근했습니다.", extra={'status': 'System'})
    logs = Log.query.order_by(Log.timestamp.desc()).limit(200).all() # 로그 200개까지 표시
    return render_template('logs.html', logs=logs)