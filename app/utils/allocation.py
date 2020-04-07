import random
import numpy as np
from app.models import db, Marker, Project, Map


class Rectangle:
    def __init__(self, center, size, rotation):
        self.center = center
        self.size = size
        self.rotation = rotation

    def to_json(self):
        w, h = self.size
        x, y = self.center
        vertices = np.array([[-w, -h], [w, -h], [w, h], [-w, h]]) / 2
        rotation = np.array([
            [np.cos(self.rotation), -np.sin(self.rotation)],
            [np.sin(self.rotation), np.cos(self.rotation)]
        ])
        rotated = np.transpose(np.dot(rotation, np.transpose(vertices)))
        return [{'x': int(round(x + v[0])), 'y': int(round(y + v[1]))} for v in rotated]


class BoothCluster:
    BASIC_UNIT = 2

    def __init__(self, map, start_point, end_point, initial_score):
        self.map = map
        self.scale = self.map.scale
        self.basic_unit_pxs = int(self.BASIC_UNIT / self.scale)

        self.start_point = start_point
        self.end_point = end_point
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        self.vector = np.array([dx, dy])
        self.rotation = np.arctan2(dy, dx)
        self.length = int((dx ** 2 + dy ** 2) ** 0.5)
        self.num_units = self.length // self.basic_unit_pxs
        self.avaliable = [True] * self.num_units

        self.initial_score = initial_score
        self.projects = []
        self.allocations = {}

    def allocate(self, project):
        for i in range(self.num_units):
            if i % 2 == 0:
                i = self.num_units // 2 + i // 2
            else:
                i = self.num_units // 2 - (i + 1) // 2

            if self.avaliable[i]:
                self.avaliable[i] = False
                self.projects.append(project)

                self.allocations[project.id] = Rectangle(
                    center=tuple(np.array(self.start_point) + self.vector * i / self.num_units),
                    size=(self.basic_unit_pxs, self.basic_unit_pxs),
                    rotation=self.rotation
                )
                return self.allocations[project.id]

    @property
    def score(self):
        return self.initial_score


def allocate():
    maps = Map.query.all()
    cluster = BoothCluster(maps[0], (0, 0), (4000, 3000), 100)
    for project in Project.query.all():
        allocation = cluster.allocate(project)
        if not allocation:
            break
        db.session.add(Marker(
            project=project,
            map=cluster.map,
            polygon=allocation.to_json()
        ))
    db.session.commit()
