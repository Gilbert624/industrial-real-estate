"""
Development Cost Breakdown Module

Industrial real estate development cost calculations for Queensland, Australia.
Includes hard costs, soft costs, and summary reporting with Brisbane/Sunshine
Coast default benchmarks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
import json


class PropertyType(Enum):
    """Industrial property types."""

    WAREHOUSE_BASIC = "basic_warehouse"
    WAREHOUSE_STANDARD = "standard_warehouse"
    WAREHOUSE_HIGH_SPEC = "high_spec_warehouse"
    DISTRIBUTION_CENTER = "distribution_center"
    MANUFACTURING = "manufacturing"
    COLD_STORAGE = "cold_storage"


# Queensland industrial development benchmarks (2024-2025)
QLD_COST_BENCHMARKS = {
    PropertyType.WAREHOUSE_BASIC: {
        "construction_rate_min": 900,
        "construction_rate_max": 1100,
        "construction_rate_typical": 1000,
    },
    PropertyType.WAREHOUSE_STANDARD: {
        "construction_rate_min": 1100,
        "construction_rate_max": 1400,
        "construction_rate_typical": 1250,
    },
    PropertyType.WAREHOUSE_HIGH_SPEC: {
        "construction_rate_min": 1400,
        "construction_rate_max": 1800,
        "construction_rate_typical": 1550,
    },
    PropertyType.DISTRIBUTION_CENTER: {
        "construction_rate_min": 1200,
        "construction_rate_max": 1600,
        "construction_rate_typical": 1400,
    },
    PropertyType.MANUFACTURING: {
        "construction_rate_min": 1300,
        "construction_rate_max": 1800,
        "construction_rate_typical": 1500,
    },
    PropertyType.COLD_STORAGE: {
        "construction_rate_min": 2000,
        "construction_rate_max": 3000,
        "construction_rate_typical": 2500,
    },
}


# Queensland government charges (indicative)
QLD_GOVERNMENT_CHARGES = {
    "brisbane": {
        "infrastructure_charge_per_sqm": 30.0,  # Industrial GFA
        "da_base_fee": 1547.0,
        "da_per_sqm_over_2000": 0.85,
        "building_approval_pct": 0.25,  # % of construction cost
        "plumbing_approval": 450.0,
        "operational_works_base": 2500.0,
    },
    "sunshine_coast": {
        "infrastructure_charge_per_sqm": 35.0,
        "da_base_fee": 1450.0,
        "da_per_sqm_over_2000": 0.80,
        "building_approval_pct": 0.25,
        "plumbing_approval": 400.0,
        "operational_works_base": 2200.0,
    },
    "moreton_bay": {
        "infrastructure_charge_per_sqm": 28.0,
        "da_base_fee": 1400.0,
        "da_per_sqm_over_2000": 0.75,
        "building_approval_pct": 0.25,
        "plumbing_approval": 380.0,
        "operational_works_base": 2000.0,
    },
}


# Professional fees benchmark (% of construction cost)
PROFESSIONAL_FEE_BENCHMARKS = {
    "architect": {"min": 2.0, "max": 5.0, "typical": 3.0},
    "structural_engineer": {"min": 1.0, "max": 2.5, "typical": 1.5},
    "civil_engineer": {"min": 1.0, "max": 2.0, "typical": 1.5},
    "mep_engineer": {"min": 1.5, "max": 3.0, "typical": 2.0},
    "quantity_surveyor": {"min": 0.5, "max": 1.5, "typical": 1.0},
    "project_manager": {"min": 2.0, "max": 5.0, "typical": 3.0},
    "town_planner": {"min": 0.3, "max": 1.0, "typical": 0.5},
    "surveyor": {"min": 0.2, "max": 0.5, "typical": 0.3},
    "geotechnical": {"min": 0.2, "max": 0.5, "typical": 0.3},
    "environmental": {"min": 0.1, "max": 0.5, "typical": 0.2},
}


@dataclass
class SiteWorksBreakdown:
    """Site works cost breakdown."""

    site_clearing: float = 0.0
    demolition: float = 0.0
    earthworks: float = 0.0
    retaining_walls: float = 0.0
    stormwater_drainage: float = 0.0
    sewer_connection: float = 0.0
    water_connection: float = 0.0
    electrical_connection: float = 0.0
    gas_connection: float = 0.0
    telecommunications: float = 0.0
    road_works: float = 0.0
    car_parking: float = 0.0
    hardstand: float = 0.0
    landscaping: float = 0.0
    fencing: float = 0.0
    signage: float = 0.0

    def total(self) -> float:
        """Calculate total site works."""
        return sum(
            [
                self.site_clearing,
                self.demolition,
                self.earthworks,
                self.retaining_walls,
                self.stormwater_drainage,
                self.sewer_connection,
                self.water_connection,
                self.electrical_connection,
                self.gas_connection,
                self.telecommunications,
                self.road_works,
                self.car_parking,
                self.hardstand,
                self.landscaping,
                self.fencing,
                self.signage,
            ]
        )

    def to_dict(self) -> Dict[str, float]:
        """Return dict representation."""
        return {
            "site_clearing": self.site_clearing,
            "demolition": self.demolition,
            "earthworks": self.earthworks,
            "retaining_walls": self.retaining_walls,
            "stormwater_drainage": self.stormwater_drainage,
            "sewer_connection": self.sewer_connection,
            "water_connection": self.water_connection,
            "electrical_connection": self.electrical_connection,
            "gas_connection": self.gas_connection,
            "telecommunications": self.telecommunications,
            "road_works": self.road_works,
            "car_parking": self.car_parking,
            "hardstand": self.hardstand,
            "landscaping": self.landscaping,
            "fencing": self.fencing,
            "signage": self.signage,
            "total": self.total(),
        }


@dataclass
class ProfessionalFeesBreakdown:
    """Professional fees breakdown."""

    architect: float = 0.0
    structural_engineer: float = 0.0
    civil_engineer: float = 0.0
    mep_engineer: float = 0.0
    quantity_surveyor: float = 0.0
    project_manager: float = 0.0
    town_planner: float = 0.0
    surveyor: float = 0.0
    geotechnical: float = 0.0
    environmental: float = 0.0
    legal_fees: float = 0.0
    valuation_fees: float = 0.0

    def total(self) -> float:
        """Calculate total professional fees."""
        return sum(
            [
                self.architect,
                self.structural_engineer,
                self.civil_engineer,
                self.mep_engineer,
                self.quantity_surveyor,
                self.project_manager,
                self.town_planner,
                self.surveyor,
                self.geotechnical,
                self.environmental,
                self.legal_fees,
                self.valuation_fees,
            ]
        )

    def to_dict(self) -> Dict[str, float]:
        """Return dict representation."""
        return {
            "architect": self.architect,
            "structural_engineer": self.structural_engineer,
            "civil_engineer": self.civil_engineer,
            "mep_engineer": self.mep_engineer,
            "quantity_surveyor": self.quantity_surveyor,
            "project_manager": self.project_manager,
            "town_planner": self.town_planner,
            "surveyor": self.surveyor,
            "geotechnical": self.geotechnical,
            "environmental": self.environmental,
            "legal_fees": self.legal_fees,
            "valuation_fees": self.valuation_fees,
            "total": self.total(),
        }


@dataclass
class GovernmentChargesBreakdown:
    """Government charges breakdown."""

    infrastructure_contribution: float = 0.0
    development_application: float = 0.0
    building_approval: float = 0.0
    plumbing_approval: float = 0.0
    operational_works: float = 0.0
    compliance_certificate: float = 0.0
    headworks_water: float = 0.0
    headworks_sewer: float = 0.0
    fire_services_levy: float = 0.0

    def total(self) -> float:
        """Calculate total government charges."""
        return sum(
            [
                self.infrastructure_contribution,
                self.development_application,
                self.building_approval,
                self.plumbing_approval,
                self.operational_works,
                self.compliance_certificate,
                self.headworks_water,
                self.headworks_sewer,
                self.fire_services_levy,
            ]
        )

    def to_dict(self) -> Dict[str, float]:
        """Return dict representation."""
        return {
            "infrastructure_contribution": self.infrastructure_contribution,
            "development_application": self.development_application,
            "building_approval": self.building_approval,
            "plumbing_approval": self.plumbing_approval,
            "operational_works": self.operational_works,
            "compliance_certificate": self.compliance_certificate,
            "headworks_water": self.headworks_water,
            "headworks_sewer": self.headworks_sewer,
            "fire_services_levy": self.fire_services_levy,
            "total": self.total(),
        }


@dataclass
class DevelopmentCostBreakdown:
    """
    Industrial development cost breakdown for Queensland projects.
    """

    # Basic project info
    project_name: str = ""
    location: str = "brisbane"  # brisbane, sunshine_coast, moreton_bay
    property_type: PropertyType = PropertyType.WAREHOUSE_STANDARD

    # Land costs
    land_area_sqm: float = 0.0
    land_price_per_sqm: float = 0.0
    land_acquisition_costs_pct: float = 6.0

    # Construction parameters
    gross_floor_area: float = 0.0
    site_coverage_pct: float = 50.0
    construction_rate_per_sqm: float = 0.0

    # Site works
    site_works: SiteWorksBreakdown = field(default_factory=SiteWorksBreakdown)

    # Contingency
    design_contingency_pct: float = 5.0
    construction_contingency_pct: float = 5.0

    # Professional fee percentages (of construction cost)
    architect_pct: float = 3.0
    structural_engineer_pct: float = 1.5
    civil_engineer_pct: float = 1.5
    mep_engineer_pct: float = 2.0
    quantity_surveyor_pct: float = 1.0
    project_manager_pct: float = 3.0
    town_planner_pct: float = 0.5
    surveyor_pct: float = 0.3
    geotechnical_pct: float = 0.3
    environmental_pct: float = 0.2

    # Fixed costs
    legal_fees: float = 25000.0
    valuation_fees: float = 5000.0
    marketing_costs: float = 0.0

    # Government charges
    government_charges: GovernmentChargesBreakdown = field(
        default_factory=GovernmentChargesBreakdown
    )

    # Finance costs (optional)
    include_finance_costs: bool = False
    finance_costs: float = 0.0

    def __post_init__(self) -> None:
        """Set default construction rate if not provided."""
        if self.construction_rate_per_sqm == 0.0 and self.property_type:
            benchmarks = QLD_COST_BENCHMARKS.get(self.property_type, {})
            self.construction_rate_per_sqm = benchmarks.get(
                "construction_rate_typical", 1250
            )

        if self.location not in QLD_GOVERNMENT_CHARGES:
            self.location = "brisbane"

    def calculate_land_costs(self) -> Dict[str, float]:
        """Calculate land purchase and acquisition costs."""
        land_purchase = self.land_area_sqm * self.land_price_per_sqm
        acquisition_costs = land_purchase * (self.land_acquisition_costs_pct / 100)
        return {
            "land_area_sqm": self.land_area_sqm,
            "land_price_per_sqm": self.land_price_per_sqm,
            "land_purchase_price": land_purchase,
            "acquisition_costs": acquisition_costs,
            "acquisition_costs_breakdown": {
                "stamp_duty_estimate": land_purchase * 0.045,
                "legal_conveyancing": land_purchase * 0.005,
                "due_diligence": land_purchase * 0.01,
            },
            "total_land_cost": land_purchase + acquisition_costs,
        }

    def calculate_construction_costs(self) -> Dict[str, float]:
        """Calculate base construction costs."""
        base_construction = self.gross_floor_area * self.construction_rate_per_sqm
        benchmarks = QLD_COST_BENCHMARKS.get(self.property_type, {})
        return {
            "gross_floor_area": self.gross_floor_area,
            "construction_rate_per_sqm": self.construction_rate_per_sqm,
            "base_construction_cost": base_construction,
            "benchmark_comparison": {
                "rate_used": self.construction_rate_per_sqm,
                "benchmark_min": benchmarks.get("construction_rate_min", 0),
                "benchmark_max": benchmarks.get("construction_rate_max", 0),
            },
        }

    def calculate_hard_costs(self) -> Dict[str, Dict]:
        """Calculate hard costs (land, construction, site works, contingency)."""
        land = self.calculate_land_costs()
        construction = self.calculate_construction_costs()
        site_works_total = self.site_works.total()
        subtotal_before_contingency = (
            construction["base_construction_cost"] + site_works_total
        )
        design_contingency = subtotal_before_contingency * (
            self.design_contingency_pct / 100
        )
        construction_contingency = subtotal_before_contingency * (
            self.construction_contingency_pct / 100
        )
        total_contingency = design_contingency + construction_contingency
        total_hard_costs = (
            land["total_land_cost"]
            + subtotal_before_contingency
            + total_contingency
        )
        return {
            "land_costs": land,
            "construction_costs": construction,
            "site_works": self.site_works.to_dict(),
            "contingency": {
                "design_contingency_pct": self.design_contingency_pct,
                "design_contingency": design_contingency,
                "construction_contingency_pct": self.construction_contingency_pct,
                "construction_contingency": construction_contingency,
                "total_contingency": total_contingency,
            },
            "summary": {
                "total_land": land["total_land_cost"],
                "total_construction": construction["base_construction_cost"],
                "total_site_works": site_works_total,
                "total_contingency": total_contingency,
                "total_hard_costs": total_hard_costs,
            },
        }

    def calculate_professional_fees(self) -> ProfessionalFeesBreakdown:
        """Calculate professional fees based on construction cost."""
        base = self.calculate_construction_costs()["base_construction_cost"]
        return ProfessionalFeesBreakdown(
            architect=base * (self.architect_pct / 100),
            structural_engineer=base * (self.structural_engineer_pct / 100),
            civil_engineer=base * (self.civil_engineer_pct / 100),
            mep_engineer=base * (self.mep_engineer_pct / 100),
            quantity_surveyor=base * (self.quantity_surveyor_pct / 100),
            project_manager=base * (self.project_manager_pct / 100),
            town_planner=base * (self.town_planner_pct / 100),
            surveyor=base * (self.surveyor_pct / 100),
            geotechnical=base * (self.geotechnical_pct / 100),
            environmental=base * (self.environmental_pct / 100),
            legal_fees=self.legal_fees,
            valuation_fees=self.valuation_fees,
        )

    def calculate_government_charges(self) -> GovernmentChargesBreakdown:
        """Calculate Queensland government charges."""
        council_rates = QLD_GOVERNMENT_CHARGES.get(
            self.location, QLD_GOVERNMENT_CHARGES["brisbane"]
        )
        base_construction = self.calculate_construction_costs()["base_construction_cost"]

        infrastructure = self.gross_floor_area * council_rates[
            "infrastructure_charge_per_sqm"
        ]
        da_fee = council_rates["da_base_fee"]
        if self.gross_floor_area > 2000:
            da_fee += (self.gross_floor_area - 2000) * council_rates[
                "da_per_sqm_over_2000"
            ]
        building_approval = base_construction * (
            council_rates["building_approval_pct"] / 100
        )

        return GovernmentChargesBreakdown(
            infrastructure_contribution=infrastructure,
            development_application=da_fee,
            building_approval=building_approval,
            plumbing_approval=council_rates["plumbing_approval"],
            operational_works=council_rates["operational_works_base"],
            compliance_certificate=1500.0,
            headworks_water=self.gross_floor_area * 5.0,
            headworks_sewer=self.gross_floor_area * 8.0,
            fire_services_levy=base_construction * 0.001,
        )

    def calculate_soft_costs(self) -> Dict[str, Dict]:
        """Calculate soft costs (professional fees, gov charges, other costs)."""
        professional_fees = self.calculate_professional_fees()
        government_charges = self.calculate_government_charges()
        other_costs = {
            "marketing": self.marketing_costs,
            "insurance_during_construction": self.calculate_construction_costs()[
                "base_construction_cost"
            ]
            * 0.01,
            "bank_fees_estimate": 0.0,
        }
        other_costs_total = sum(other_costs.values())
        total_soft_costs = (
            professional_fees.total()
            + government_charges.total()
            + other_costs_total
        )
        if self.include_finance_costs:
            total_soft_costs += self.finance_costs

        return {
            "professional_fees": professional_fees.to_dict(),
            "government_charges": government_charges.to_dict(),
            "other_costs": other_costs,
            "finance_costs": self.finance_costs if self.include_finance_costs else 0.0,
            "total_soft_costs": total_soft_costs,
        }

    def calculate_total_development_cost(self) -> Dict[str, Dict]:
        """Calculate total development cost and summary metrics."""
        hard_costs = self.calculate_hard_costs()
        soft_costs = self.calculate_soft_costs()
        total_hard = hard_costs["summary"]["total_hard_costs"]
        total_soft = soft_costs["total_soft_costs"]
        total_development_cost = total_hard + total_soft

        hard_cost_pct = (
            (total_hard / total_development_cost * 100)
            if total_development_cost > 0
            else 0
        )
        soft_cost_pct = (
            (total_soft / total_development_cost * 100)
            if total_development_cost > 0
            else 0
        )
        cost_per_sqm_gfa = (
            total_development_cost / self.gross_floor_area
            if self.gross_floor_area > 0
            else 0
        )
        cost_per_sqm_land = (
            total_development_cost / self.land_area_sqm
            if self.land_area_sqm > 0
            else 0
        )

        return {
            "project_name": self.project_name,
            "location": self.location,
            "property_type": self.property_type.value,
            "hard_costs": hard_costs,
            "soft_costs": soft_costs,
            "summary": {
                "total_hard_costs": total_hard,
                "total_soft_costs": total_soft,
                "total_development_cost": total_development_cost,
                "hard_cost_percentage": hard_cost_pct,
                "soft_cost_percentage": soft_cost_pct,
                "cost_per_sqm_gfa": cost_per_sqm_gfa,
                "cost_per_sqm_land": cost_per_sqm_land,
            },
            "areas": {
                "land_area_sqm": self.land_area_sqm,
                "gross_floor_area": self.gross_floor_area,
                "site_coverage_pct": self.site_coverage_pct,
            },
        }

    def generate_cost_summary_table(self) -> List[Dict[str, str]]:
        """Generate summary rows for Streamlit display."""
        result = self.calculate_total_development_cost()
        rows: List[Dict[str, str]] = []

        # Hard costs
        rows.append({"Category": "HARD COSTS", "Item": "", "Amount": "", "Percentage": ""})
        hard = result["hard_costs"]
        rows.append(
            {
                "Category": "",
                "Item": "Land Purchase",
                "Amount": hard["land_costs"]["land_purchase_price"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Land Acquisition Costs",
                "Amount": hard["land_costs"]["acquisition_costs"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Base Construction",
                "Amount": hard["construction_costs"]["base_construction_cost"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Site Works",
                "Amount": hard["site_works"]["total"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Contingency",
                "Amount": hard["contingency"]["total_contingency"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Subtotal Hard Costs",
                "Amount": hard["summary"]["total_hard_costs"],
                "Percentage": f"{result['summary']['hard_cost_percentage']:.1f}%",
            }
        )

        # Soft costs
        rows.append({"Category": "SOFT COSTS", "Item": "", "Amount": "", "Percentage": ""})
        soft = result["soft_costs"]
        rows.append(
            {
                "Category": "",
                "Item": "Professional Fees",
                "Amount": soft["professional_fees"]["total"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Government Charges",
                "Amount": soft["government_charges"]["total"],
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Other Costs",
                "Amount": sum(soft["other_costs"].values()),
                "Percentage": "",
            }
        )
        if self.include_finance_costs:
            rows.append(
                {
                    "Category": "",
                    "Item": "Finance Costs",
                    "Amount": soft["finance_costs"],
                    "Percentage": "",
                }
            )
        rows.append(
            {
                "Category": "",
                "Item": "Subtotal Soft Costs",
                "Amount": soft["total_soft_costs"],
                "Percentage": f"{result['summary']['soft_cost_percentage']:.1f}%",
            }
        )

        # Total
        rows.append({"Category": "TOTAL", "Item": "", "Amount": "", "Percentage": ""})
        rows.append(
            {
                "Category": "",
                "Item": "Total Development Cost",
                "Amount": result["summary"]["total_development_cost"],
                "Percentage": "100%",
            }
        )
        rows.append(
            {
                "Category": "",
                "Item": "Cost per sqm (GFA)",
                "Amount": result["summary"]["cost_per_sqm_gfa"],
                "Percentage": "",
            }
        )
        return rows

    def to_json(self) -> str:
        """Export full breakdown to JSON."""
        result = self.calculate_total_development_cost()
        return json.dumps(result, indent=2, default=str)


def create_sunshine_coast_warehouse_example() -> DevelopmentCostBreakdown:
    """Example: Sunshine Coast 4,200sqm warehouse development."""
    site_works = SiteWorksBreakdown(
        site_clearing=25000,
        earthworks=150000,
        stormwater_drainage=80000,
        sewer_connection=35000,
        water_connection=25000,
        electrical_connection=45000,
        road_works=120000,
        car_parking=85000,
        hardstand=180000,
        landscaping=35000,
        fencing=45000,
    )
    return DevelopmentCostBreakdown(
        project_name="Sunshine Coast Industrial Warehouse",
        location="sunshine_coast",
        property_type=PropertyType.WAREHOUSE_STANDARD,
        land_area_sqm=8500,
        land_price_per_sqm=350,
        gross_floor_area=4200,
        site_coverage_pct=49.4,
        construction_rate_per_sqm=1250,
        site_works=site_works,
        design_contingency_pct=5.0,
        construction_contingency_pct=5.0,
        legal_fees=30000,
        valuation_fees=8000,
    )
