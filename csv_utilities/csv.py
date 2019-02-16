from contextlib import contextmanager


class CSVException(BaseException):
    pass


class CSV(object):
    def __init__(self, path):
        self.path = path

        with open(path, 'r') as csv:
            raw = csv.readlines()

        self.rows = [
            l.rstrip('\n').split(',')
            for l in raw
        ]
        self.headers = self.rows.pop(0)
        self._init_header_indices()
        self.columns = zip(*self.rows)

    def _init_header_indices(self):
        self.header_indices = {
            self.headers[i]: i
            for i in range(len(self.headers))
        }

    def column(self, column_name):
        try:
            column_index = self.header_indices[column_name]
        except KeyError:
            raise CSVException('Column "%s" does not exist' % column_name)

        return self.columns[column_index]

    def set_column(self, column_name, values):
        try:
            column_index = self.header_indices[column_name]
        except KeyError:
            raise CSVException('Column "%s" does not exist' % column_name)

        if not len(self.columns[column_index]) == len(values):
            raise CSVException('Cannot set unequal column values')

        self.columns[column_index] = values

    def row(self, index):
        return self.rows[index]

    def row_dict(self, index):
        row = self.row(index)

        return {
            self.headers[i]: row[i]
            for i in range(len(self.headers))
        }

    def sum(self, column_name):
        column = self.column(column_name)

        try:
            return sum([float(x) for x in column])
        except ValueError:
            return sum(column)

    def save(self, path):
        with open(path, 'w') as f:
            f.write(','.join(self.headers))

            for row in self.rows:
                f.write(','.join(row))

        self.path = path

    @classmethod
    def show(cls, items):
        for item in items:
            print(item)


    @contextmanager
    def update_rows_from_columns(self):
        yield
        self.rows = zip(*self.columns)

    @contextmanager
    def update_columns_from_rows(self):
        yield
        self.rows = zip(*self.columns)

    # translation
    def move_column(self, column_name, to):
        """
        [0, 1, 2, 3, 4, 5]
        move_column("1", 3)
        [0, 2, 3, 1, 4, 5]
        """
        # remove header
        header_index = self.header_indices[column_name]
        self.headers.pop(header_index)

        # remove column for header
        column = self.columns.pop(header_index)

        # insert header
        self.headers.insert(to, column_name)

        # insert column for header and update rows after
        with self.update_rows_from_columns():
            self.columns.insert(to, column)

        # update indices
        self._init_header_indices()

    def order_columns(self, header_order):
        """reorders columns"""
        if not set(header_order) == set(self.headers):
            CSVException(header_order)

        self.headers = header_order

        with self.update_rows_from_columns():
            self.columns = [self.column(header) for header in header_order]

        self._init_header_indices()

    def _transform_column(self, column_name, transform_fn):
        # WARNING: DOES NOT UPDATE ROWS
        new_column = [transform_fn(column_value) for column_value in self.column(column_name)]

        self.set_column(column_name, new_column)

    def transform_columns(self, transformations):
        """given a dict of header: transformation_fn, transforms columns"""
        with self.update_rows_from_columns():
            for column_name, transformation_fn in transformations.items():
                self._transform_column(column_name, transformation_fn)


    def transform_headers(self, new_headers):
        if not len(new_headers) == len(self.headers):
            raise CSVException(new_headers)

        self.headers = new_headers
        self._init_header_indices()
