from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

metadata = MetaData(schema="online_platform")
Base = automap_base(metadata=metadata)