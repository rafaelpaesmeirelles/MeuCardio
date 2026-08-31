from app.core.db import SessionLocal
from app.models.audit import AuditLog
from app.services.whatsapp_assistant import purge_expired_data
def purge_once(*,session_factory=SessionLocal,origin="maintenance_command"):
 db=session_factory()
 try:
  n=purge_expired_data(db);db.add(AuditLog(user_id=None,action="whatsapp_retention_purged",entity="whatsapp_transport_data",detail={"deleted":n,"origin":origin}));db.commit();return n
 except Exception:db.rollback();raise
 finally:db.close()
def main():print(f"whatsapp_transport_deleted={purge_once()}")
if __name__=="__main__":main()
