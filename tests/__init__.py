import random
from config import Config
from app import create_app
from app.models import db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestBase:
    def setup_class(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self._app_context = self.app.app_context()
        self._app_context.push()
        db.create_all()
        db.session.execute('pragma foreign_keys=ON')

    def teardown_class(self):
        db.session.remove()
        db.drop_all()
        self._app_context.pop()


class MutationOperator:
    def mutate(self, line):
        raise NotImplementedError()


class SwapMutator(MutationOperator):
    def mutate(self, line):
        p1 = random.randrange(len(line))
        p2 = random.randrange(len(line))
        characters = list(line)
        characters[p1] = line[p2]
        characters[p2] = line[p1]
        return ''.join(characters)


class BitFlipMutator(MutationOperator):
    def mutate(self, line):
        characters = list(line)
        # choose the character to be bit flipped
        pos = random.randrange(len(line))
        char = characters[pos]
        # bit flip
        mask = 1 << random.randrange(7)
        char = chr((ord(char) & ~mask) | (~ord(char) & mask))
        # apply change to result
        characters[pos] = char
        return ''.join(characters)


class TrimMutator(MutationOperator):
    def mutate(self, line):
        characters = list(line)
        characters.pop(random.randrange(len(line)))
        return ''.join(characters)


class MultiMutator(MutationOperator):
    def __init__(self, mutators):
        super().__init__()
        self.mutators = mutators

    def mutate(self, line):
        if len(line) < 1:
            return line
        mutated = line
        while mutated == line:
            mutated = random.choice(self.mutators).mutate(line)
        return mutated


mutator = MultiMutator([
    SwapMutator(),
    BitFlipMutator(),
    TrimMutator()
])
