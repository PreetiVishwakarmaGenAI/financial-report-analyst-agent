from enum import Enum


class TaskType(str, Enum):
    SUMMARY = "summary"
    COMPARISON = "comparison"
    RISK_ANALYSIS = "risk_analysis"
    FINANCIAL_METRIC = "financial_metric"
    GENERAL_QA = "general_qa"