from pydantic import BaseModel
from typing import List, Optional

class Recruit(BaseModel):
    job_id: Optional[str] 
    job_company_id: Optional[str] = None
    source_job_url: Optional[str] = None
    job_is_new_arrival: Optional[bool] = False
    job_employment_type: Optional[List[str]] = None
    job_permanent_employment_type: Optional[List[str]] = None
    job_position_count: Optional[str] = None
    job_title: Optional[str] = None
    job_sub_title: Optional[str] = None
    job_description: Optional[str] = None
    job_requirement: Optional[str] = None
    job_address: Optional[str] = None
    job_commute_info: Optional[str] = None
    job_office_name: Optional[str] = None
    job_working_location: Optional[str] = None
    job_summary_salary: Optional[str] = None
    job_tags: Optional[List[str]] = None
    job_business_content: Optional[str] = None
    job_published_at: Optional[str] = None
    job_company_name: Optional[str] = None
    job_salary: Optional[str] = None
    job_working_style: Optional[str] = None
    job_working_hour: Optional[str] = None
    job_holiday: Optional[str] = None
    job_trial_period: Optional[str] = None
    job_welfare_insurance: Optional[str] = None
    job_welfare_benefit : Optional[str] = None
    job_working_environment: Optional[str] = None
    job_industry : Optional[str] = None
    job_company_hp_url: Optional[str] = None
    job_apply_info: Optional[str] = None
    job_max_salary: Optional[int] = None
    job_min_salary: Optional[int] = None
    job_tags: Optional[List[str]] = None
    job_business_detail: Optional[str] = None
    job_salary_unit: Optional[str] = None
    source_job_url: Optional[str] = None
    