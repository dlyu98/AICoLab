from backend.app.core.constants import SAFETY_NOTICE
from backend.app.models import AgentResponse, Evidence, Recommendation
from backend.app.services.data_loader import dataset_profile


def ask_operations(question: str) -> AgentResponse:
    q = question.lower()
    profile = dataset_profile()
    if "sql" in q or "readmission" in q:
        answer = "Use encounters filtered to inpatient discharges, left join readmission encounters within 30 days, then group by risk tier or service line."
        sql = "SELECT p.patient_id, COUNT(e.encounter_id) AS encounters FROM patients p LEFT JOIN encounters e USING (patient_id) GROUP BY p.patient_id;"
    elif "cohort" in q:
        answer = "Cohort logic: include synthetic patients with an inpatient encounter and at least one abnormal lab or documented social barrier."
        sql = "SELECT DISTINCT patient_id FROM encounters WHERE type = 'inpatient';"
    else:
        answer = "The synthetic dataset supports patient summaries, care gaps, readmission risk demos, and data-quality review."
        sql = "SELECT table_name, row_count FROM synthetic_data_dictionary;"
    return AgentResponse(agent_name="Healthcare Operations Copilot", summary=answer, recommendations=[Recommendation(action="Validate generated SQL against your warehouse schema before use.", priority="medium", reason="Schema names and SQL dialects vary across healthcare analytics environments.")], evidence=[Evidence(source="synthetic_dataset_profile", snippet=str(profile))], confidence="medium", safety_notice=SAFETY_NOTICE, structured_output={"dataset_profile": profile, "suggested_sql": sql, "question": question})
