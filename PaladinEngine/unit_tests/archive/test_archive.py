import unittest

from PaladinEngine.archive.archive import Archive


class MockObject(object):
    def __init__(self, mock_field: object = 42):
        self.field = mock_field

    def __str__(self):
        return 'Mock(field = {})'.format(self.field)


class ArchiveUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.archive = Archive()
        cls.all_vars = {}

    def setUp(self) -> None:
        super().setUp()

        # Clear the archive.
        self.archive.clear()

    def test_archive_store(self):
        # Create a mock object.
        mock_object = MockObject()

        # Store the mock object.
        self.archive.store('mock_object')

        # Change a field in mock object.
        mock_object.field = MockObject()

        # Store the field.
        self.archive.store('mock_object.field')

        print(self.archive.retrieve('mock_object'))

        # Create a recursive mock field and store once.
        mock_object_2 = MockObject(MockObject(MockObject(MockObject())))

        print(mock_object_2.field.field.field)

        self.archive.store('mock_object_2.field.field.field')

        print(self.archive)


if __name__ == '__main__':
    unittest.main()
