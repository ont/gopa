class T:
    def __init__(self, parser):
        self.parser = parser

    def must_parse(self, value):
        try:
            self.parser.parse(value)
            return True
        except Exception as e:
            print(e)
            return False
