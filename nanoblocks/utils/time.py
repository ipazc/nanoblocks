import pandas as pd

from datetime import datetime
from tzlocal import get_localzone


SYSTEM_TIMEZONE = str(get_localzone())


def now(tz=SYSTEM_TIMEZONE):
    return pd.to_datetime(datetime.utcnow()).tz_localize("UTC").tz_convert(tz)
