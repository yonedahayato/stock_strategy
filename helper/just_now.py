import datetime
from pytz import timezone

utc_now = datetime.datetime.now(timezone('UTC'))
jst_now = utc_now.astimezone(timezone('Asia/Tokyo'))
