class ActionFixture(object):
    def process(self, table):
        for row in table.rows[1:]:
            action = str(row[0])
            if action == 'start':
                name = str(row[1])
                fixture = self.engine.loader.load(name)
