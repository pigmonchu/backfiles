class ModelMixin(object):
    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    @property
    def as_dict(self):
        return {column: getattr(self, column) for column in self.columns if column not in ['timestamp_insert', 'timestamp_update', 'user_update']}
