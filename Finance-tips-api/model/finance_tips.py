"""
Modèles de base de données pour Finance-tips
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Text, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship, backref
from config.db import db
from config.constant import ACCOUNT_TYPES, USER_ROLES

# Table d'association pour la relation many-to-many entre User et Role
user_roles = Table('user_roles', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Role(db.Model):
    """Modèle pour les rôles utilisateurs"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model):
    """Modèle pour les utilisateurs"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    account_type = Column(String(20), nullable=False, default=ACCOUNT_TYPES['ENTITY'])
    company_name = Column(String(100))  # Pour les comptes Company
    company_address = Column(Text)
    company_tax_id = Column(String(50))  # Numéro de TVA ou équivalent
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relations
    roles = relationship('Role', secondary=user_roles, backref='users')
    receipts = relationship('Receipt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    brands = relationship('Brand', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    calculations = relationship('Calculation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    newsletters = relationship('Newsletter', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Vérifie si l'utilisateur a un rôle spécifique"""
        return any(role.name == role_name for role in self.roles)
    
    def add_role(self, role_name):
        """Ajoute un rôle à l'utilisateur"""
        role = Role.query.filter_by(name=role_name).first()
        if role and role not in self.roles:
            self.roles.append(role)
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'account_type': self.account_type,
            'company_name': self.company_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'roles': [role.name for role in self.roles]
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Brand(db.Model):
    """Modèle pour les marques/tampons personnalisés"""
    __tablename__ = 'brands'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    logo_url = Column(String(255))
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))
    font_family = Column(String(50))
    slogan = Column(String(200))
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(120))
    website = Column(String(255))
    tax_id = Column(String(50))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'font_family': self.font_family,
            'slogan': self.slogan,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'tax_id': self.tax_id,
            'is_default': self.is_default
        }
    
    def __repr__(self):
        return f'<Brand {self.name}>'

class Receipt(db.Model):
    """Modèle pour les reçus"""
    __tablename__ = 'receipts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'))
    receipt_number = Column(String(50), unique=True, nullable=False)
    template_type = Column(String(20), default='simple')
    customer_name = Column(String(100))
    customer_email = Column(String(120))
    customer_phone = Column(String(20))
    customer_address = Column(Text)
    items = Column(JSON)  # Liste des articles [{name, quantity, price, tax}]
    subtotal = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default='EUR')
    payment_method = Column(String(50))
    notes = Column(Text)
    status = Column(String(20), default='draft')  # draft, sent, paid, cancelled
    issued_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation
    brand = relationship('Brand', backref='receipts')
    
    def calculate_totals(self):
        """Calcule les totaux du reçu"""
        if self.items:
            self.subtotal = sum(item.get('quantity', 0) * item.get('price', 0) for item in self.items)
            self.tax_amount = sum(item.get('tax', 0) for item in self.items)
            self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'receipt_number': self.receipt_number,
            'template_type': self.template_type,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'items': self.items,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'brand': self.brand.to_dict() if self.brand else None
        }
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number}>'

class Calculation(db.Model):
    """Modèle pour sauvegarder les calculs financiers"""
    __tablename__ = 'calculations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    calculation_type = Column(String(50), nullable=False)  # savings_plan, loan_duration, budget_simulation
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'calculation_type': self.calculation_type,
            'input_data': self.input_data,
            'result_data': self.result_data,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Calculation {self.calculation_type} - {self.id}>'

class FinancialTip(db.Model):
    """Modèle pour les conseils financiers/blog"""
    __tablename__ = 'financial_tips'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    category = Column(String(50))
    tags = Column(JSON)  # Liste de tags
    author_id = Column(Integer, ForeignKey('users.id'))
    image_url = Column(String(255))
    is_published = Column(Boolean, default=False)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relations
    author = relationship('User', backref='articles')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'summary': self.summary,
            'category': self.category,
            'tags': self.tags,
            'author': self.author.username if self.author else None,
            'image_url': self.image_url,
            'is_published': self.is_published,
            'views_count': self.views_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<FinancialTip {self.title}>'

class Newsletter(db.Model):
    """Modèle pour les inscriptions à la newsletter"""
    __tablename__ = 'newsletters'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    is_subscribed = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    unsubscribed_at = Column(DateTime)
    preferences = Column(JSON)  # Préférences de contenu
    
    def __repr__(self):
        return f'<Newsletter {self.email}>'

class AuditLog(db.Model):
    """Modèle pour l'audit des actions importantes"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation
    user = relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'