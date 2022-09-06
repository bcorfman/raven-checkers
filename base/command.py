class Command(object):
    def __init__(self, **props):
        self.add = props.get('add') or []
        self.remove = props.get('remove') or []
