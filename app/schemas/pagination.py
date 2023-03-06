from typing import Dict
from math import ceil
from pydantic import (
    BaseModel,
    root_validator
)


class Pagination(BaseModel):
    current_page: int
    per_page: int
    total_records: int
    total_pages: int = 0

    @root_validator
    def compute_total_pages(cls, values) -> Dict:

        total_pages = ceil(values["total_records"] / values["per_page"])

        values["total_pages"] = total_pages

        return values
