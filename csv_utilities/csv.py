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
        self._header_indices = {
            self.headers[i]: i
            for i in range(len(self.headers))
        }
        self.columns = zip(*self.rows)

    def column(self, column_name):
        try:
            column_index = self._header_indices[column_name]
        except KeyError:
            raise CSVException('Column "%s" does not exist' % column_name)

        return self.columns[column_index]

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

    @classmethod
    def show(cls, items):
        for item in items:
            print(item)
