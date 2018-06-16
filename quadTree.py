from math import sqrt
from typing import Union, Tuple
from collections import namedtuple

Bounds = namedtuple('Bounds', 'x y w h')
Circle = namedtuple('Circle', 'x y r')


def circle_intersect_rect(circle: Union[Circle, Tuple[float, float, float]],
                          rect: Union[Bounds, Tuple[float, float, float, float]]) -> bool:
    circle, rect = Circle(*circle), Bounds(*rect)

    delta_x = circle.x - max(rect.x, min(circle.x, rect.x + rect.w))
    delta_y = circle.y - max(rect.y, min(circle.y, rect.y + rect.h))

    return (delta_x * delta_x + delta_y * delta_y) < (circle.r * circle.r)


def distance(obj1, obj2) -> float:
    return sqrt((obj1.x - obj2.x) * (obj1.x - obj2.x) + (obj1.y - obj2.y) * (obj1.y - obj2.y))


class QuadTree:
    def __init__(self, bounds: Union[Bounds, Tuple[float, float, float, float]], members: list=None, max_for_node: int=4):
        if members is None:
            members = []

        self.bounds: Bounds = Bounds(*bounds)

        self.max_for_node: int = max_for_node

        self.top_left: 'QuadTree' = None
        self.top_right: 'QuadTree' = None
        self.bottom_left: 'QuadTree' = None
        self.bottom_right: 'QuadTree' = None

        self.members = []
        self.insert(members)

    def __iter__(self) -> 'QuadTree':
        self._index = -1
        self._parts = []
        if self.divided:
            self._parts = [self.top_left, self.top_right, self.bottom_left, self.bottom_right]
        return self

    def __next__(self) -> 'QuadTree':
        if self._index < len(self._parts) - 1:
            self._index += 1
            return self._parts[self._index]
        else:
            raise StopIteration

    def insert(self, members: Union[list, tuple]) -> list:
        not_inserted = []

        for member in members:
            assert hasattr(member, 'x')
            assert hasattr(member, 'y')

            if not self.contains(member):
                not_inserted.append(member)
                continue

            if not self.divided:
                if len(self.members) > self.max_for_node - 1:
                    self.divide()
                else:
                    self.members.append(member)

            if self.divided:
                for tree in self:
                    if tree.contains(member):
                        tree.insert([member])
                        break
                else:
                    not_inserted.append(member)

        return not_inserted

    def divide(self) -> None:
        x = self.bounds.x
        y = self.bounds.y
        width = self.bounds.w / 2
        height = self.bounds.h / 2

        self.top_left = QuadTree(Bounds(x, y, width, height), [], max_for_node=self.max_for_node)
        self.top_right = QuadTree(Bounds(x + width, y, width, height), [], max_for_node=self.max_for_node)
        self.bottom_left = QuadTree(Bounds(x, y + height, width, height), [], max_for_node=self.max_for_node)
        self.bottom_right = QuadTree(Bounds(x + width, y + height, width, height), [], max_for_node=self.max_for_node)

        for member in self.members:
            for tree in self:
                if tree.contains(member):
                    tree.insert([member])
                    break

            self.members.remove(member)

    def contains(self, obj) -> bool:
        return self.bounds.x < obj.x < (self.bounds.x + self.bounds.w) and \
               self.bounds.y < obj.y < (self.bounds.y + self.bounds.h)

    def get_members_in_circle(self, circle: Circle) -> list:
        members = []
        if circle_intersect_rect(circle, self.bounds):
            if self.is_leaf:
                for member in self.members:
                    if distance(member, circle):
                        members.append(member)

            else:
                for tree in self:
                    members += tree.get_members_in_circle(circle)

        return members

    @property
    def divided(self) -> bool:
        return bool(self.top_left or self.top_right or self.bottom_left or self.bottom_right)

    @property
    def is_leaf(self) -> bool:
        return not self.divided
