import os


class Simpledb:
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return ("<" + self.__class__.__name__ +
        " file='" + str(self.filename) + "'" +
        ">")
    
    def insert(self, key, value):
        f = open(self.filename, 'a')
        f.write(str(key) + '\t' + str(value) + '\n')
        f.close()

    def select_one(self, key):
        f = open(self.filename, 'r')
        for line in f:
            (i, j) = line.split('\t', 1)
            if i == key:
                f.close()
                return j[:-1]
        f.close()

    def delete(self, key):
        f = open(self.filename, 'r')
        f2 = open('Exchange.txt', 'w')
        success = 0
        for row in f:
            (i, j) = row.split('\t', 1)
            if i != key:
                f2.write(row)
            else:
                success = 1

        f2.close()
        f.close()
        os.replace('Exchange.txt', self.filename)

        if success == 1:
            return True
        else:
            return False

    def update(self, key, value):
        f = open(self.filename, 'r')
        f2 = open('Exchange.txt', 'w')
        successful = 0
        for row in f:
            (i, j) = row.split('\t', 1)
            if i == key:
                f2.write(key + '\t' + value + '\n')
                successful = 1
            else:
                f2.write(row)
        f.close()
        f2.close()
        os.replace('Exchange.txt', self.filename)

        if successful == 1:
            return True
        else:
            return False


