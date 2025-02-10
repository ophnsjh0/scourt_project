from datetime import datetime
import pytz

startdatetime_str = f"{request.args.get('startdate')}T{request.args.get('starttime')}"
enddatetime_str = f"{request.args.get('enddate')}T{request.args.get('endtime')}"
startdatetime_obj = datetime.strptime(startdatetime_str, "%Y-%m-%dT%H:%M")
enddatetime_obj = datetime.strptime(enddatetime_str, "%Y-%m-%dT%H:%M")
utc_timezone = pytz.utc
kst_timezone = pytz.timezone("Asia/seoul")
startdatetime_utc = utc_timezone.localize(startdatetime_obj)
startdatetime_kst = startdatetime_utc.astimezone(kst_timezone)
startdatetime_format_kst = startdatetime_kst.strftime("%Y-%m-%dT%H:%M")
enddatetime_utc = utc_timezone.localize(enddatetime_obj)
enddatetime_kst = enddatetime_utc.astimezone(kst_timezone)
enddatetime_format_kst = enddatetime_kst.strftime("%Y-%m-%dT%H:%M")

i['startdatetime'] = startdatetime_format_kst
i['enddatetime'] = enddatetime_format_kst

