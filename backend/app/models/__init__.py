from app.models.user import User  # noqa: F401
from app.models.content import Document, DocumentRevision  # noqa: F401
from app.models.drug import Drug  # noqa: F401
from app.models.round import Patient, PatientProblem, PatientNote, PatientAISuggestion  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.rag import DocumentChunk, AIConversation, AIMessage  # noqa: F401
from app.models.gallery import GalleryImage  # noqa: F401
from app.models.favorite import Favorite  # noqa: F401
from app.models.password_reset import PasswordResetToken  # noqa: F401
from app.models.lab_test import LabTest  # noqa: F401
from app.models.evidence import EvidenceRecord  # noqa: F401
from app.models.study import ScientificStudy  # noqa: F401
from app.models.clinical_docs import Prescription, DocumentTemplate, GeneratedDocument, Appointment  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.service_order import ServiceOrder, ServiceOrderPatient  # noqa: F401
from app.models.partner_course import PartnerCourse, CourseMaterial, CoursePayment  # noqa: F401
from app.models.guideline import Guideline, GuidelineLink  # noqa: F401
from app.models.checklist import DischargeChecklist, DischargeChecklistRun  # noqa: F401
from app.models.study_track import StudyTrack, StudyTrackProgress  # noqa: F401
from app.models.compartilhamento import DocumentShareLink  # noqa: F401
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide  # noqa: F401
from app.models.receituario import (  # noqa: F401
    ControlledSubstance, PrescriptionType, PrescriptionRule,
    PrescriptionRecipient, PrescriptionDocument,
)
from app.models.assinatura import DocumentoEmitido  # noqa: F401
from app.models.cmed import CmedVersao, CmedApresentacao  # noqa: F401
from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado  # noqa: F401
from app.models.agenda import (  # noqa: F401
    AppointmentCommunication, AppointmentResource, AvailabilityException,
    AvailabilityRule, CalendarDelegation, CalendarIntegration, CalendarLocation,
    CalendarOutboxEvent, ExternalContact, ExternalPatientLink, IntegrationOAuthState,
    MobilityPreference, SchedulingResource,
    SchedulingService, ServiceResourceRequirement,
)
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation  # noqa: F401
from app.models.prontuario import ClinicalEncounter, PatientClinicalItem, PatientExamResult  # noqa: F401
