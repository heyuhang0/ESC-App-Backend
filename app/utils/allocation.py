import math
import numpy as np
from app.models import db, Marker, Project, Map


def apply_rotation(vector, rotation):
    rotation = np.array([
        [np.cos(rotation), -np.sin(rotation)],
        [np.sin(rotation), np.cos(rotation)]
    ])
    rotated = np.transpose(np.dot(rotation, np.transpose(vector)))
    return rotated


class Rectangle:
    def __init__(self, center, size, rotation):
        self.center = center
        self.size = size
        self.rotation = rotation

    def to_json(self):
        w, h = self.size
        x, y = self.center
        vertices = np.array([[-w, -h], [w, -h], [w, h], [-w, h]]) / 2
        rotated = apply_rotation(vertices, self.rotation)
        return [{'x': int(round(x + v[0])), 'y': int(round(y + v[1]))} for v in rotated]


class BoothCluster:
    BASIC_UNIT = 2

    def __init__(self, map, start_point, end_point, initial_score, rows=1):
        self.map = map
        self.scale = self.map.scale
        self.basic_unit_pxs = int(self.BASIC_UNIT / self.scale)

        self.start_point = start_point
        self.end_point = end_point
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        self.vector = np.array([dx, dy])
        self.rotation = np.arctan2(dy, dx)
        self.center = tuple(np.array(start_point) + self.vector / 2)
        self.length = int((dx ** 2 + dy ** 2) ** 0.5)
        self.width = rows * self.basic_unit_pxs
        self.columns = self.length // self.basic_unit_pxs
        self.rows = rows
        self.avaliable = [[True] * self.columns for _ in range(rows)]

        self.initial_score = initial_score
        self.projects = []
        self.allocations = {}

    def get_unit_pos(self, x, y, x_size=1, y_size=1):
        relative_pos = np.array([x + x_size/2 - self.columns/2, y + y_size/2 - self.rows/2])
        relative_pos *= self.basic_unit_pxs
        relative_pos_rotated = apply_rotation(relative_pos, self.rotation)
        final_pos = np.array(self.center) + relative_pos_rotated
        return tuple(final_pos)

    def get_unit_score(self, x, y, x_size=1, y_size=1):
        if not self.check_availability(x, y, x_size, y_size):
            return 0
        # a booth should have at least one side facing out
        if x != 0 and x+x_size != self.columns and y != 0 and y+y_size != self.rows:
            return 0
        occupancy_x = abs(x + x_size/2 - self.columns/2) / (self.columns/2)
        return (1 - 0.3 * occupancy_x) * self.initial_score

    def check_availability(self, x, y, x_size=1, y_size=1):
        if x_size > self.columns or y_size > self.rows:
            return False
        for m in range(x, x+x_size):
            for n in range(y, y+y_size):
                if m >= self.columns or n >= self.rows or not self.avaliable[n][m]:
                    return False
        return True

    def allocate_by_unit(self, x_size, y_size):
        best_unit = None
        best_unit_score = 0
        for m in range(self.rows - y_size + 1):
            for n in range(self.columns - x_size + 1):
                score = self.get_unit_score(n, m, x_size, y_size)
                if score > best_unit_score:
                    best_unit = (n, m)
                    best_unit_score = score
        return best_unit, best_unit_score

    def get_units_required(self, project: Project):
        x_size = math.ceil(project.space_x / self.BASIC_UNIT)
        y_size = math.ceil(project.space_y / self.BASIC_UNIT)
        return x_size, y_size

    def allocate(self, project: Project) -> Rectangle:
        x_size, y_size = self.get_units_required(project)
        unit_allocation, score = self.allocate_by_unit(x_size, y_size)
        if score > 0:
            x, y = unit_allocation
            for m in range(x, x+x_size):
                for n in range(y, y+y_size):
                    self.avaliable[n][m] = False
            self.projects.append(project)
            self.allocations[project.id] = Rectangle(
                center=self.get_unit_pos(x, y, x_size, y_size),
                size=(self.basic_unit_pxs * x_size - 5, self.basic_unit_pxs * y_size - 5),
                rotation=self.rotation
            )
            return self.allocations[project.id]

    def score(self, project: Project):
        x_size, y_size = self.get_units_required(project)
        return self.allocate_by_unit(x_size, y_size)[1]


class Allocator:
    def __init__(self, clusters: BoothCluster):
        self.clusters = clusters

    def allocate(self, project: Project):
        fittest_cluster = max(self.clusters, key=lambda c: c.score(project))
        allocation = fittest_cluster.allocate(project)
        if allocation:
            return fittest_cluster.map, allocation.to_json()
        # case when allocation failed
        return None, None


def allocate():
    maps = Map.query.all()
    allocator = Allocator([
        BoothCluster(maps[0], (2400, 2150), (3100, 2150), 100, 3),
        BoothCluster(maps[0], (2400, 1800), (3000, 1800), 100, 3),
        BoothCluster(maps[0], (3150, 1600), (3150, 2000), 80),
        BoothCluster(maps[0], (2300, 1700), (2300, 2000), 80),
        BoothCluster(maps[0], (1980, 2100), (2420, 2500), 80, 2),
        BoothCluster(maps[0], (3160, 2470), (3600, 2040), 80, 2),
        BoothCluster(maps[0], (3470, 1780), (3650, 1780), 70),
        BoothCluster(maps[0], (1845, 1800), (1980, 1800), 70),
        BoothCluster(maps[0], (3260, 1560), (3465, 1450), 40),
        BoothCluster(maps[0], (1700, 1600), (1700, 1950), 50),
        BoothCluster(maps[0], (1830, 1530), (2150, 1530), 50),
        BoothCluster(maps[0], (2620, 2550), (2900, 2550), 50),
        BoothCluster(maps[1], (1800, 1000), (3250, 1000), 60),
        BoothCluster(maps[1], (1180, 1760), (2230, 2300), 50),
        BoothCluster(maps[1], (2320, 2330), (2770, 2330), 50),
        BoothCluster(maps[1], (2880, 2290), (3700, 1870), 50),
        BoothCluster(maps[1], (1870, 2400), (2200, 2690), 40),
        BoothCluster(maps[1], (2940, 2670), (3460, 2200), 40),
    ])
    skipped = []
    for project in Project.query.all():
        allocated_map, allocated_polygon = allocator.allocate(project)
        if not allocated_map:
            skipped.append(project)
            continue
        db.session.add(Marker(
            project=project,
            map=allocated_map,
            polygon=allocated_polygon
        ))
    db.session.commit()
    return skipped
