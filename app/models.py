import datetime

from sqlalchemy import ForeignKey, Column
from sqlalchemy import Integer, Float, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from app import db
from flask import current_app
from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature


class User(db.Model):
    __talbename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(128), index=True, unique=True, comment='email address')
    password = Column(String(128))
    full_name = Column(String(128))
    is_admin = Column(Boolean, default=0)

    project = relationship('Project', uselist=False, back_populates='user')

    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            # valid token, but expired
            return None
        except BadSignature:
            # invalid token
            return None
        user = User.query.get(data['id'])
        return user


class Project(db.Model):
    __talbename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    type = Column(String(128))

    space_x = Column(Float, comment='in meters')
    space_y = Column(Float, comment='in meters')
    sapce_z = Column(Float, comment='in meters')

    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship('User', back_populates='project')
    updated_on = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    prototype_x = Column(Float, default=0, comment='in meters')
    prototype_y = Column(Float, default=0, comment='in meters')
    prototype_z = Column(Float, default=0, comment='in meters')
    prototype_weight = Column(Float, default=0, comment='in kg')

    power_points_count = Column(Integer, default=0)
    pedestall_big_count = Column(Integer, default=0)
    pedestall_small_count = Column(Integer, default=0)
    pedestall_description = Column(Text, default='')
    monitor_count = Column(Integer, default=0)
    tv_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    chair_count = Column(Integer, default=0)
    hdmi_to_vga_adapter_count = Column(Integer, default=0)
    hdmi_cable_count = Column(Integer, default=0)

    remark = Column(Text, default='')
    marker = relationship('Marker', uselist=False, back_populates='project')


class Marker(db.Model):
    __tablename__ = 'marker'
    id = Column(Integer, primary_key=True)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='marker')

    polygon = Column(Text, default='[]')
