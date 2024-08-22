from sqlalchemy import Column, INTEGER, VARCHAR

from bot import MODEL, SESSION


class Auth(MODEL):
    __tablename__ = 'auth'
    auth_id = Column(INTEGER, primary_key=True, autoincrement=True)
    guild_id = Column(VARCHAR(255))
    owner_id = Column(VARCHAR(50))
    authorized_id = Column(VARCHAR(500))

    def save(self):
        SESSION.add(self)
        SESSION.flush()

    def commit(self):
        self.save()
        SESSION.commit()

    def retrieve(self, include_owner=True):
        ids: list = [int(i) for i in self.authorized_id.split(',')] if self.authorized_id else []
        if include_owner:
            ids.append(int(self.owner_id))
        return ids

    def retrieve_raw(self, include_owner=True):
        ids: list = [i for i in self.authorized_id.split(',')] if self.authorized_id else []
        if include_owner:
            ids.append(self.owner_id)
        return ids
