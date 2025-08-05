from pydantic import BaseModel, Field,field_validator
import re
from pydantic_core.core_schema import ValidationInfo

class QAEnrichedArticle(BaseModel):
    has_two_links: bool = Field(..., description="Exactly two inline links are present.")
    has_two_images: bool = Field(..., description="Exactly two images are present in the correct positions.")
    has_valid_alt_text: bool = Field(..., description="Alt text exists, is descriptive, and under 125 characters.")
    follows_brand_voice: bool = Field(..., description="Brand tone and voice were followed.")
    accepted: bool = Field(..., description="True only if all above are true.")
    score: float = Field(..., ge=0, le=10, description="Rating from 0–10 based on enrichment quality")

    @field_validator('accepted')
    @classmethod
    def accept_only_if_all_true(cls, v, info: ValidationInfo):
        values = info.data
        required_flags = ['has_two_links', 'has_two_images', 'has_valid_alt_text', 'follows_brand_voice']
        if any(values.get(flag) is False for flag in required_flags):
            if v:
                raise ValueError("Cannot accept article if any pass criteria is false.")
            return False
        return v

    @field_validator('score')
    @classmethod
    def ensure_score_matches_acceptance(cls, v, info: ValidationInfo):
        values = info.data
        accepted = values.get('accepted', False)
        if accepted and v < 7:
            raise ValueError("Accepted articles must score at least 7.")
        if not accepted and v >= 7:
            raise ValueError("Rejected articles must score below 7.")
        return v