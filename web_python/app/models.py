# /fortify_web_analyzer/app/models.py

from app import db
from sqlalchemy import UniqueConstraint
from datetime import datetime

# --- Rule과 Language를 연결하는 연관 테이블 (변경 없음) ---
rule_language_association = db.Table('rule_language_association',
    db.Column('rule_id', db.Integer, db.ForeignKey('rules.id'), primary_key=True),
    db.Column('language_id', db.Integer, db.ForeignKey('languages.id'), primary_key=True)
)

# --- RulePack 모델 (변경 없음) ---
class RulePack(db.Model):
    __tablename__ = 'rule_packs'
    id = db.Column(db.Integer, primary_key=True)
    pack_name = db.Column(db.String(255), nullable=False)
    # --- ✨ unique=True 속성을 제거합니다. ---
    pack_id = db.Column(db.String(255), nullable=False) 
    pack_version = db.Column(db.String(100))
    # --- ✨ 이제 location이 고유 식별자 역할을 합니다. ---
    location = db.Column(db.String(1024), unique=True, nullable=False)

    def __repr__(self):
        return f'<RulePack {self.pack_name} ({self.pack_version})>'

# --- Rule 모델 (변경 없음) ---
class Rule(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(255), nullable=False)
    rule_pack_id = db.Column(db.Integer, db.ForeignKey('rule_packs.id'), nullable=False)
    rule_pack = db.relationship('RulePack', backref=db.backref('rules', lazy='dynamic'))
    __table_args__ = (UniqueConstraint('rule_name', 'rule_pack_id', name='_rule_name_pack_id_uc'),)
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

# --- ✨ Log 모델 (수정 확인) ---
class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    # 'level'이 아닌 'status'를 사용합니다.
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    traceback = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Log {self.timestamp} [{self.status}] {self.message[:50]}>'