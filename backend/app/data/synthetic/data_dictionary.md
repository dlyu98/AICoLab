# Synthetic Data Dictionary

All files contain synthetic demonstration data only and must not be treated as real PHI.

| File | Grain | Key fields | Purpose |
| --- | --- | --- | --- |
| `patients.json` | One row per synthetic patient | `patient_id`, demographics, `problems` | Patient selector and summary context |
| `encounters.json` | One row per encounter | `encounter_id`, `patient_id`, `type`, `date`, `reason`, `status` | Utilization, readmission, follow-up logic |
| `labs.json` | One row per lab result | `code`, `name`, `value`, `flag` | Abnormal result and risk rules |
| `medications.json` | One row per medication | `name`, `status`, `dose` | Medication summary and polypharmacy rules |
| `notes.json` | One row per synthetic note | `note_type`, `text` | Note extraction examples |
| `social_determinants.json` | One row per social domain | `domain`, `status`, `detail` | Social risk and care gap rules |
