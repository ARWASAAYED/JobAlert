from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Job:
    source: str
    id: str
    title: str
    company: str
    location: str
    url: str
    posted_text: str = ""            # "5 minutes ago"
    posted_at: str = ""              # "2026-11-04 17:12"
    description: Optional[str] = None
    remote_search: bool = False      # اتجابت من بحث ريموت
    applicants: str = ""
    score: int = 0                   # 0 - 100
    verdict: str = ""                # Strong Fit, Good Fit, Moderate Fit
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    cv_suggestions: List[str] = field(default_factory=list)
    work_type: str = ""              # Remote, Hybrid, On-site (set by filters.work_type)
    country: str = ""                # Egypt, Worldwide, USA, etc. (extracted from location)

    @property
    def key(self):
        return f"{self.source}:{self.id}"
