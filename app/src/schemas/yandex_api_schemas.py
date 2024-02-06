from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessInfo:
    id: int
    name: str


@dataclass(frozen=True)
class CampaignInfo:
    id: int
    client_id: int
    domain: str
    business: BusinessInfo

