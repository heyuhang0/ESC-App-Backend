import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column
from sqlalchemy import Integer, Float, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from flask import current_app
from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

db = SQLAlchemy()


class User(db.Model):
    __talbename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(128), index=True, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(128), default='')
    is_admin = Column(Boolean, default=False)

    projects = relationship('Project', back_populates='creator')

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = custom_app_context.hash(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password_hash)

    @property
    def token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return str(s.dumps({'id': self.id}), encoding='utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        data = s.loads(token)
        user = User.query.get(data['id'])
        return user


class Project(db.Model):
    __talbename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    type = Column(String(128))

    space_x = Column(Float, comment='in meters')
    space_y = Column(Float, comment='in meters')
    space_z = Column(Float, comment='in meters')

    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship('User', back_populates='projects')
    updated_on = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    prototype_x = Column(Float, default=0, comment='in meters')
    prototype_y = Column(Float, default=0, comment='in meters')
    prototype_z = Column(Float, default=0, comment='in meters')
    prototype_weight = Column(Float, default=0, comment='in kg')

    power_points_count = Column(Integer, default=0)
    pedestal_big_count = Column(Integer, default=0)
    pedestal_small_count = Column(Integer, default=0)
    pedestal_description = Column(Text, default='')
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

    map_id = Column(Integer, ForeignKey('map.id'))
    map = relationship('Map', back_populates='markers')

    polygon_json = Column(Text, default='[]')

    def _clean_contour(self, contours):
        clean_contours = [{
            'x': int(point['x']),
            'y': int(point['y'])
        } for point in contours]
        return clean_contours

    @property
    def polygon(self):
        return self._clean_contour(json.loads(self.polygon_json))

    @polygon.setter
    def polygon(self, contours):
        self.polygon_json = json.dumps(self._clean_contour(contours))

    @property
    def centre(self):
        coords = self.polygon
        if len(coords) >= 3:
            cx, cy, area = 0.0, 0.0, 0.0
            for i in range(len(coords)):
                x_i = coords[i]['x']
                y_i = coords[i]['y']
                x_ip1 = coords[(i+1) % len(coords)]['x']
                y_ip1 = coords[(i+1) % len(coords)]['y']
                cx += (x_i + x_ip1) * (x_i * y_ip1 - x_ip1 * y_i)
                cy += (y_i + y_ip1) * (x_i * y_ip1 - x_ip1 * y_i)
                area += 0.5 * (x_i * y_ip1 - x_ip1 * y_i)
            cx /= 6 * area
            cy /= 6 * area
            return {
                'x': int(cx),
                'y': int(cy)
            }
        else:
            return coords[0]


class Map(db.Model):
    __tablename__ = 'map'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    url = Column(String(256))
    level = Column(Integer)
    scale = Column(Float, comment="meter per pixel")
    markers = relationship('Marker', back_populates='map')
