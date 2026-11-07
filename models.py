from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Job:
    source: str
    id: str
    title: str
    company: str
    location: str
    url: str
    posted_text: str = ""            # "5 minutes ago"
    description: Optional[str] = None
    remote_search: bool = False      # اتجابت من بحث ريموت
    applicants: str = ""

    @property
    def key(self):
        return f"{self.source}:{self.id}"
