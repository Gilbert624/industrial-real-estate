"""
Due Diligence Report Generator
Creates professional investment analysis reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io
from utils.financial_model import FinancialModel, format_currency, format_percentage

class DDReportGenerator:
    """Generate comprehensive due diligence reports"""
    
    def __init__(self, project, db_manager):
        """
        Initialize report generator
        
        Args:
            project: DDProject object
            db_manager: DatabaseManager instance
        """
        self.project = project
        self.db = db_manager
        
        # Prepare model parameters
        self.model_params = {
            'purchase_price': project.purchase_price or 0,
            'acquisition_costs': project.acquisition_costs or 0,
            'construction_cost': project.construction_cost or 0,
            'construction_duration_months': project.construction_duration_months or 12,
            'contingency_percentage': project.contingency_percentage or 10.0,
            'equity_percentage': project.equity_percentage or 30.0,
            'debt_percentage': project.debt_percentage or 70.0,
            'interest_rate': project.interest_rate or 6.0,
            'loan_term_years': project.loan_term_years or 25,
            'estimated_monthly_rent': project.estimated_monthly_rent or 0,
            'rent_growth_rate': project.rent_growth_rate or 3.0,
            'occupancy_rate': project.occupancy_rate or 95.0,
            'operating_expense_ratio': project.operating_expense_ratio or 30.0,
            'holding_period_years': project.holding_period_years or 10,
            'exit_cap_rate': project.exit_cap_rate or 6.5
        }
        
        # Calculate financial model
        self.model = FinancialModel(self.model_params)
        self.returns = self.model.calculate_returns()
        self.scenarios = self.model.calculate_three_scenarios()
    
    def generate_report(self, output_path=None):
        """
        Generate complete investment report
        
        Args:
            output_path: File path to save PDF. If None, returns BytesIO buffer
            
        Returns:
            File path or BytesIO buffer
        """
        # Create buffer or file
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
        else:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Container for flowables
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#4a90e2'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )
        
        # ========== Cover Page ==========
        elements.append(Spacer(1, 1.5*inch))
        
        title = Paragraph("Investment Analysis Report", title_style)
        elements.append(title)
        
        elements.append(Spacer(1, 0.3*inch))
        
        project_title = Paragraph(
            f"<para align=center><b>{self.project.name}</b></para>",
            ParagraphStyle('ProjectTitle', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER)
        )
        elements.append(project_title)
        
        elements.append(Spacer(1, 0.2*inch))
        
        if self.project.location:
            location = Paragraph(
                f"<para align=center>{self.project.location}</para>",
                ParagraphStyle('Location', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER)
            )
            elements.append(location)
        
        elements.append(Spacer(1, 0.5*inch))
        
        date_text = Paragraph(
            f"<para align=center>Report Date: {datetime.now().strftime('%B %d, %Y')}</para>",
            styles['Normal']
        )
        elements.append(date_text)
        
        elements.append(Spacer(1, 0.3*inch))
        
        status_color = {
            'Under Review': colors.HexColor('#4ECDC4'),
            'Approved': colors.HexColor('#45B7D1'),
            'Rejected': colors.HexColor('#FF6B6B'),
            'On Hold': colors.HexColor('#FFA07A')
        }.get(self.project.status, colors.gray)
        
        status_para = Paragraph(
            f"<para align=center><b>Status: {self.project.status}</b></para>",
            ParagraphStyle('Status', parent=styles['Normal'], fontSize=14, 
                         alignment=TA_CENTER, textColor=status_color)
        )
        elements.append(status_para)
        
        elements.append(PageBreak())
        
        # ========== Executive Summary ==========
        elements.append(Paragraph("Executive Summary", heading_style))
        
        # Investment recommendation
        irr = self.returns.get('irr', 0)
        
        if irr and irr >= 20:
            recommendation = "STRONG BUY"
            rec_color = colors.HexColor('#45B7D1')
        elif irr and irr >= 15:
            recommendation = "BUY"
            rec_color = colors.HexColor('#4ECDC4')
        elif irr and irr >= 12:
            recommendation = "HOLD"
            rec_color = colors.HexColor('#FFA07A')
        else:
            recommendation = "PASS"
            rec_color = colors.HexColor('#FF6B6B')
        
        rec_para = Paragraph(
            f"<para align=center><b>Investment Recommendation: {recommendation}</b></para>",
            ParagraphStyle('Recommendation', parent=styles['Normal'], fontSize=16,
                         alignment=TA_CENTER, textColor=rec_color, spaceAfter=20)
        )
        elements.append(rec_para)
        
        # Key highlights
        summary_text = f"""
        This report presents a comprehensive financial analysis of the {self.project.name} development opportunity 
        in {self.project.location or 'the target market'}. The project involves a {self.project.property_type or 'industrial development'} 
        with an estimated total development cost of {format_currency(self.returns['cash_flow_model']['development_costs']['total_development_cost'])}.
        """
        
        elements.append(Paragraph(summary_text, body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key metrics table
        elements.append(Paragraph("Key Investment Metrics", subheading_style))
        
        metrics_data = [
            ['Metric', 'Value', 'Assessment'],
            ['IRR', format_percentage(irr), '✓ Strong' if irr >= 15 else '⚠ Below Target'],
            ['NPV', format_currency(self.returns.get('npv')), '✓ Positive' if self.returns.get('npv', 0) > 0 else '✗ Negative'],
            ['Equity Multiple', f"{self.returns.get('equity_multiple', 0):.2f}x", '✓ Good' if self.returns.get('equity_multiple', 0) >= 2 else '⚠ Below 2x'],
            ['Equity Required', format_currency(self.returns.get('total_equity_invested')), ''],
            ['Total Profit', format_currency(self.returns.get('total_profit')), ''],
            ['DSCR (Avg)', f"{self.returns.get('avg_dscr', 0):.2f}x", '✓ Healthy' if self.returns.get('avg_dscr', 0) >= 1.25 else '✗ Low']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        elements.append(PageBreak())
        
        # ========== Project Overview ==========
        elements.append(Paragraph("Project Overview", heading_style))
        
        overview_data = [
            ['Attribute', 'Details'],
            ['Project Name', self.project.name],
            ['Location', self.project.location or 'N/A'],
            ['Property Type', self.project.property_type or 'N/A'],
            ['Land Area', f"{self.project.land_area_sqm:,.0f} sqm" if self.project.land_area_sqm else 'N/A'],
            ['Building Area', f"{self.project.building_area_sqm:,.0f} sqm" if self.project.building_area_sqm else 'N/A'],
            ['Zoning', self.project.zoning or 'N/A'],
            ['Construction Duration', f"{self.project.construction_duration_months} months" if self.project.construction_duration_months else 'N/A']
        ]
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 4*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(overview_table)
        elements.append(Spacer(1, 0.2*inch))
        
        if self.project.description:
            elements.append(Paragraph("Description", subheading_style))
            elements.append(Paragraph(self.project.description, body_style))
        
        elements.append(PageBreak())
        
        # ========== Financial Analysis ==========
        elements.append(Paragraph("Financial Analysis", heading_style))
        
        # Development costs
        elements.append(Paragraph("Development Cost Breakdown", subheading_style))
        
        costs = self.returns['cash_flow_model']['development_costs']
        
        cost_data = [
            ['Cost Category', 'Amount'],
            ['Land Acquisition', format_currency(costs['land_cost'])],
            ['Acquisition Costs', format_currency(costs['acquisition_costs'])],
            ['Hard Costs', format_currency(costs['hard_costs'])],
            ['Contingency', format_currency(costs['contingency'])],
            ['Soft Costs', format_currency(costs['soft_costs'])],
            ['Total Development Cost', format_currency(costs['total_development_cost'])]
        ]
        
        cost_table = Table(cost_data, colWidths=[3.5*inch, 2.5*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(cost_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Financing structure
        elements.append(Paragraph("Financing Structure", subheading_style))
        
        financing = self.returns['cash_flow_model']['financing']
        
        fin_data = [
            ['Component', 'Amount', '% of Total'],
            ['Equity Investment', format_currency(financing['equity_required']), 
             f"{self.project.equity_percentage:.0f}%"],
            ['Debt Financing', format_currency(financing['debt_amount']), 
             f"{self.project.debt_percentage:.0f}%"],
            ['Capitalized Interest', format_currency(self.returns['cash_flow_model']['capitalized_interest']), 
             ''],
            ['Total Loan at Completion', format_currency(self.returns['cash_flow_model']['total_loan_at_completion']), '']
        ]
        
        fin_table = Table(fin_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(fin_table)
        elements.append(Spacer(1, 0.3*inch))
        
        elements.append(PageBreak())
        
        # ========== Scenario Analysis ==========
        elements.append(Paragraph("Scenario Analysis", heading_style))
        
        scenario_text = """
        Three scenarios have been modeled to assess the range of potential outcomes:
        """
        elements.append(Paragraph(scenario_text, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        scenario_data = [
            ['Scenario', 'IRR', 'NPV', 'Equity Multiple'],
            ['Pessimistic', 
             format_percentage(self.scenarios['pessimistic'].get('irr')),
             format_currency(self.scenarios['pessimistic'].get('npv')),
             f"{self.scenarios['pessimistic'].get('equity_multiple', 0):.2f}x"],
            ['Base Case', 
             format_percentage(self.scenarios['base'].get('irr')),
             format_currency(self.scenarios['base'].get('npv')),
             f"{self.scenarios['base'].get('equity_multiple', 0):.2f}x"],
            ['Optimistic', 
             format_percentage(self.scenarios['optimistic'].get('irr')),
             format_currency(self.scenarios['optimistic'].get('npv')),
             f"{self.scenarios['optimistic'].get('equity_multiple', 0):.2f}x"]
        ]
        
        scenario_table = Table(scenario_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
        scenario_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#e8f4f8')),  # Highlight base case
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(scenario_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Scenario assumptions
        assumptions_text = """
        <b>Scenario Assumptions:</b><br/>
        • <b>Pessimistic:</b> +15% construction cost, -15% rent, -5pts occupancy, +1.0pts exit cap<br/>
        • <b>Base Case:</b> Current parameter assumptions<br/>
        • <b>Optimistic:</b> -10% construction cost, +20% rent, +3pts occupancy, -0.5pts exit cap
        """
        elements.append(Paragraph(assumptions_text, body_style))
        
        elements.append(PageBreak())
        
        # ========== Risk Assessment ==========
        elements.append(Paragraph("Risk Assessment", heading_style))
        
        risk_text = """
        The following key risks have been identified for this investment:
        """
        elements.append(Paragraph(risk_text, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Risk matrix
        risk_data = [
            ['Risk Category', 'Probability', 'Impact', 'Mitigation'],
            ['Construction Cost Overrun', 'Medium', 'High', 'Fixed-price contracts, contingency buffer'],
            ['Market Rental Decline', 'Low', 'High', 'Conservative rent assumptions, multi-tenant strategy'],
            ['Financing Risk', 'Low', 'Medium', 'Pre-arranged facilities, strong covenant'],
            ['Timing/Delay Risk', 'Medium', 'Medium', 'Experienced contractor, buffer in schedule'],
            ['Market Competition', 'Medium', 'Low', 'Strong location, quality product']
        ]
        
        risk_table = Table(risk_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 2.4*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        elements.append(PageBreak())
        
        # ========== Conclusion & Recommendation ==========
        elements.append(Paragraph("Conclusion & Recommendation", heading_style))
        
        # Generate conclusion based on metrics
        conclusion_text = f"""
        Based on comprehensive financial analysis, this investment opportunity presents 
        a {recommendation.lower()} case for investment. The project demonstrates:
        <br/><br/>
        • Projected IRR of {format_percentage(irr)}, {'exceeding' if irr >= 15 else 'below'} 
        the target hurdle rate of 15%<br/>
        • Equity multiple of {self.returns.get('equity_multiple', 0):.2f}x over the 
        {self.project.holding_period_years}-year holding period<br/>
        • Net Present Value of {format_currency(self.returns.get('npv'))}<br/>
        • Average DSCR of {self.returns.get('avg_dscr', 0):.2f}x, 
        {'demonstrating strong' if self.returns.get('avg_dscr', 0) >= 1.25 else 'indicating potential'} 
        debt service capacity<br/>
        <br/>
        """
        
        if irr >= 20:
            conclusion_text += """
            The strong projected returns, combined with favorable market conditions and 
            manageable risk profile, make this a compelling investment opportunity. 
            We recommend proceeding to final due diligence and contract negotiation.
            """
        elif irr >= 15:
            conclusion_text += """
            The projected returns meet our investment criteria. While there are execution 
            risks to manage, the fundamental opportunity is sound. We recommend proceeding 
            with careful monitoring of key assumptions.
            """
        elif irr >= 12:
            conclusion_text += """
            The projected returns are marginally acceptable. Consider opportunities to 
            enhance value through cost reduction or revenue optimization before proceeding. 
            Recommend additional analysis and negotiation on terms.
            """
        else:
            conclusion_text += """
            The projected returns do not meet our investment criteria at current assumptions. 
            Significant improvements in cost structure or revenue potential would be required 
            to make this opportunity attractive. We recommend passing on this opportunity 
            or substantially renegotiating terms.
            """
        
        elements.append(Paragraph(conclusion_text, body_style))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Final recommendation box
        rec_box = Paragraph(
            f"<para align=center><b>FINAL RECOMMENDATION: {recommendation}</b></para>",
            ParagraphStyle('FinalRec', parent=styles['Normal'], fontSize=14,
                         alignment=TA_CENTER, textColor=rec_color, 
                         borderColor=rec_color, borderWidth=2, borderPadding=10)
        )
        elements.append(rec_box)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            """<i>This report is for informational purposes only and does not constitute 
            investment advice. All figures are estimates based on assumptions that may change. 
            Actual results may vary materially from projections.</i>""",
            ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=9, 
                         alignment=TA_JUSTIFY, textColor=colors.grey)
        )
        elements.append(disclaimer)
        
        # Build PDF
        doc.build(elements)
        
        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer
