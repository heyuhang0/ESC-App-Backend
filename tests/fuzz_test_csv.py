import io
import random
from tests import TestBase, mutator
from app.models import db, User


def fuzz_csv(template: str):
    lines = template.split('\n')
    newlines = []
    for _ in range(random.randrange(2 * len(lines))):
        newlines.append(mutator.mutate(random.choice(lines)))
    return '\n'.join(newlines)


class TestCSV(TestBase):
    def setup_class(self):
        super().setup_class(self)
        self.admin = User(
            email='admin@test.com',
            password='adminpassword',
            full_name='Admin',
            is_admin=True
        )
        db.session.add(self.admin)
        db.session.commit()

    def test(self):
        print()
        csv_template = ''.join(open('tests/project_requirements.csv', 'r').readlines())
        print(csv_template)
        last_csv = csv_template
        for _ in range(100):
            print('='*100)
            random_csv = fuzz_csv(csv_template if random.random() < 0.5 else last_csv)
            last_csv = random_csv
            print(random_csv)
            rv = self.client.post(
                '/projects',
                data={'file': (io.BytesIO(bytes(random_csv, encoding='utf-8')), 'test.csv')},
                headers={'Authorization': 'Bearer ' + self.admin.token},
                content_type='multipart/form-data'
            )
            print(rv.json)
            assert rv.status_code != 500
