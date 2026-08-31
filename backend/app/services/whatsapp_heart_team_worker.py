import signal,time
from app.core.config import settings
from app.services.whatsapp_jobs import process_pending_heart_team_jobs
from app.services.heart_team import process_pending_analysis_jobs
from app.commands.purge_expired_whatsapp_data import purge_once
STOP=False
def stop(*_):
 global STOP;STOP=True
def run_round(last_retention_run=None,now=None):
 current=time.monotonic() if now is None else now;r=process_pending_heart_team_jobs(5);r["direct_heart_team"]=process_pending_analysis_jobs(2)
 if last_retention_run is None or current-last_retention_run>=max(60,settings.whatsapp_retention_purge_interval_seconds):r["retention_deleted"]=purge_once(origin="whatsapp_worker");last_retention_run=current
 return r,last_retention_run
def run():
 signal.signal(signal.SIGTERM,stop);last=None
 while not STOP:
  _,last=run_round(last);time.sleep(max(5,settings.whatsapp_heart_team_worker_interval_seconds))
if __name__=="__main__":run()
