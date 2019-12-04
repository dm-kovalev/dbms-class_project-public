from cherrypy.process import wspbus, plugins
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from . import Base


class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus, connection_string):
        super(SAEnginePlugin, self).__init__(bus)

        self.sa_engine = None
        self.session = None
        self.connection_string = connection_string

    def start(self):
        self.sa_engine = create_engine(self.connection_string)
        Base.prepare(self.sa_engine, reflect=True, schema="online_platform")

        self.bus.subscribe("bind", self.bind)
        self.bus.subscribe("commit", self.commit)

    def stop(self):
        self.bus.unsubscribe("bind", self.bind)
        self.bus.unsubscribe("commit", self.commit)

        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self):
        self.session = Session(bind=self.sa_engine)
        return self.session

    def commit(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()