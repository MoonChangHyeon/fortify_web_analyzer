# /fortify_web_analyzer/app/models.py

from app import db
from sqlalchemy import UniqueConstraint # UniqueConstraint를 가져옵니다.

# --- Rule과 Language를 연결하는 연관 테이블 (변경 없음) ---
rule_language_association = db.Table('rule_language_association',
    db.Column('rule_id', db.Integer, db.ForeignKey('rules.id'), primary_key=True),
    db.Column('language_id', db.Integer, db.ForeignKey('languages.id'), primary_key=True)
)

# --- ✨ 신규: RulePack 정보를 저장할 테이블 모델 ---
class RulePack(db.Model):
    __tablename__ = 'rule_packs'
    id = db.Column(db.Integer, primary_key=True)
    pack_name = db.Column(db.String(255), nullable=False)
    pack_id = db.Column(db.String(255), unique=True, nullable=False) # PackID는 고유해야 함
    pack_version = db.Column(db.String(100))

    def __repr__(self):
        return f'<RulePack {self.pack_name} ({self.pack_version})>'

# --- ✨ 수정: Rule 모델 구조 변경 ---
class Rule(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(255), nullable=False) # unique=True 속성 제거

    # 어떤 RulePack에 속하는지 연결 (Foreign Key)
    rule_pack_id = db.Column(db.Integer, db.ForeignKey('rule_packs.id'), nullable=False)
    rule_pack = db.relationship('RulePack', backref=db.backref('rules', lazy='dynamic'))

    # (rule_name, rule_pack_id) 조합이 유일하도록 복합 제약조건 설정
    __table_args__ = (UniqueConstraint('rule_name', 'rule_pack_id', name='_rule_name_pack_id_uc'),)
    
    # Language와의 관계는 변경 없음
    languages = db.relationship('Language', secondary=rule_language_association, lazy='subquery',
                                backref=db.backref('rules', lazy=True))

# --- ExternalMapping 모델 (변경 없음) ---
class ExternalMapping(db.Model):
    __tablename__ = 'external_mappings'
    id = db.Column(db.Integer, primary_key=True)
    standard_info = db.Column(db.String(255), nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('rules.id'), nullable=False)
    rule = db.relationship('Rule', backref=db.backref('mappings', lazy=True, cascade="all, delete-orphan"))

# --- Language 모델 (변경 없음) ---
class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Language {self.name}>'