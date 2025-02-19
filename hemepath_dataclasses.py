from pydantic import BaseModel


class ReportType(BaseModel):
    dx_type: str


class FlowSummary(BaseModel):
    fcm_summary: str


class SomaticMutations(BaseModel):
    gene: str
    dna_change: str
    prot_change: str
    vaf: str
    alt_type: str


class HemepathResults(BaseModel):
    mrn: str
    report_type: str
    fcm: str
    history: str
    dx_category: str
    somatic_muts: list[SomaticMutations]
