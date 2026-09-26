"""PDF Security Assessment Report Generator using ReportLab."""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

from app.models import Assessment, SecurityCheck, Finding, Evidence
from app.reports.html_generator import get_safe_reports_directory


class NumberedCanvas(canvas.Canvas):
    """Custom canvas that performs two-pass rendering to dynamically compute total page count."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        if self._pageNumber == 1:
            # Skip header and footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        self.drawString(
            54,
            letter[1] - 36,
            "SIH26163 Security Assessment Report  •  World Monitor Defensive Evaluation",
        )
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running Footer
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(54, 32, "CLASSIFICATION: AUTHORIZED SECURITY ASSESSMENT")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def generate_pdf_report(
    assessment: Assessment,
    checks: list[SecurityCheck],
    findings: list[Finding],
    evidence_items: list[Evidence],
    output_filename: Optional[str] = None,
) -> tuple[str, str]:
    """Generate a multi-page PDF assessment report using ReportLab.

    Returns:
        tuple[str, str]: (filename, absolute_file_path)
    """
    reports_dir = get_safe_reports_directory()
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if not output_filename:
        output_filename = f"security_assessment_report_A{assessment.id}_{timestamp_str}.pdf"

    safe_filename = Path(output_filename).name
    destination_path = (reports_dir / safe_filename).resolve()

    if not str(destination_path).startswith(str(reports_dir)):
        raise ValueError("Path traversal attempt detected in PDF report generation output path.")

    doc = SimpleDocTemplate(
        str(destination_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    code_style = ParagraphStyle(
        "ReportCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0284c7"),
        backColor=colors.HexColor("#f8fafc"),
        borderPadding=4,
        spaceAfter=6,
    )

    is_demo = (
        assessment.target_type == "DEMO"
        or "9000" in str(assessment.target_url)
        or "demo-target" in str(assessment.target_url)
    )

    story = []

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    story.append(Spacer(1, 20))
    story.append(
        Paragraph(
            "<font color='#0284c7'><b>SIH26163 • SECURITY ASSESSMENT PLATFORM</b></font>",
            subtitle_style,
        )
    )
    story.append(Paragraph("SECURITY ASSESSMENT REPORT", title_style))
    story.append(
        Paragraph(
            "Automated & Defensive Security Evaluation Dossier",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=15))

    # Metadata Table
    meta_data = [
        [
            Paragraph("<b>Target Application:</b>", body_style),
            Paragraph("World Monitor", body_style),
            Paragraph("<b>Assessment ID:</b>", body_style),
            Paragraph(f"#{assessment.id}", body_style),
        ],
        [
            Paragraph("<b>Target Host URL:</b>", body_style),
            Paragraph(assessment.target_url, body_style),
            Paragraph("<b>Classification:</b>", body_style),
            Paragraph(assessment.target_type, body_style),
        ],
        [
            Paragraph("<b>Assessment Status:</b>", body_style),
            Paragraph(assessment.status, body_style),
            Paragraph("<b>Duration:</b>", body_style),
            Paragraph(f"{assessment.duration_seconds or 0:.2f}s", body_style),
        ],
        [
            Paragraph("<b>Assessment Date:</b>", body_style),
            Paragraph(
                assessment.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                if assessment.created_at
                else "N/A",
                body_style,
            ),
            Paragraph("<b>Generated:</b>", body_style),
            Paragraph(
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                body_style,
            ),
        ],
    ]

    meta_table = Table(meta_data, colWidths=[1.4 * inch, 2.1 * inch, 1.3 * inch, 2.2 * inch])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Controlled Demo Warning Banner
    if is_demo:
        demo_banner_data = [
            [
                Paragraph(
                    "<font color='#b45309'><b>CONTROLLED DEMONSTRATION TARGET</b></font><br/>"
                    "<font color='#92400e'><b>IMPORTANT:</b> Findings in this assessment belong to the controlled demonstration target (port 9000) and must not be interpreted as vulnerabilities in World Monitor.</font>",
                    body_style,
                )
            ]
        ]
        demo_banner_table = Table(demo_banner_data, colWidths=[7.0 * inch])
        demo_banner_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#f59e0b")),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        story.append(demo_banner_table)

    story.append(Spacer(1, 40))
    story.append(
        Paragraph(
            "<b>TESTING CLASSIFICATION: AUTHORIZED SECURITY ASSESSMENT</b>",
            ParagraphStyle("Class", parent=body_style, fontName="Helvetica-Bold", textColor=colors.HexColor("#0f172a")),
        )
    )
    story.append(
        Paragraph(
            "SIH26163 Security Assessment Platform • Pair-Programming Security Architecture",
            body_style,
        )
    )

    story.append(PageBreak())

    # ==========================================
    # 2. EXECUTIVE SUMMARY
    # ==========================================
    story.append(Paragraph("01. Executive Summary", section_heading))
    story.append(
        Paragraph(
            f"The SIH26163 Security Assessment Engine conducted a defensive security assessment against "
            f"<b>{assessment.target_url}</b> (Target Mode: <b>{assessment.target_type}</b>). "
            f"The engine executed a total of <b>{assessment.total_checks}</b> security check modules evaluating "
            f"edge headers, CORS policies, session cookie attributes, TLS enforcement, information disclosure sinks, "
            f"and source code pattern sinks.",
            body_style,
        )
    )
    story.append(Spacer(1, 8))

    # Stats Summary Table
    summary_data = [
        [
            Paragraph("<b>Total Checks</b>", body_style),
            Paragraph("<b>Passed</b>", body_style),
            Paragraph("<b>Failed</b>", body_style),
            Paragraph("<b>Manual Review</b>", body_style),
            Paragraph("<b>Total Findings</b>", body_style),
        ],
        [
            Paragraph(f"<b>{assessment.total_checks}</b>", body_style),
            Paragraph(f"<font color='#16a34a'><b>{assessment.passed_checks}</b></font>", body_style),
            Paragraph(f"<font color='#dc2626'><b>{assessment.failed_checks}</b></font>", body_style),
            Paragraph(f"<font color='#9333ea'><b>{assessment.manual_checks}</b></font>", body_style),
            Paragraph(f"<b>{len(findings)}</b>", body_style),
        ],
    ]
    summary_table = Table(summary_data, colWidths=[1.4 * inch] * 5)
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ffffff")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Severity Breakdown Table
    sev_data = [
        [
            Paragraph("<font color='#dc2626'><b>CRITICAL</b></font>", body_style),
            Paragraph("<font color='#ea580c'><b>HIGH</b></font>", body_style),
            Paragraph("<font color='#d97706'><b>MEDIUM</b></font>", body_style),
            Paragraph("<font color='#65a30d'><b>LOW</b></font>", body_style),
            Paragraph("<font color='#0284c7'><b>INFO</b></font>", body_style),
        ],
        [
            Paragraph(f"<b>{assessment.critical_findings}</b>", body_style),
            Paragraph(f"<b>{assessment.high_findings}</b>", body_style),
            Paragraph(f"<b>{assessment.medium_findings}</b>", body_style),
            Paragraph(f"<b>{assessment.low_findings}</b>", body_style),
            Paragraph(f"<b>{assessment.info_findings}</b>", body_style),
        ],
    ]
    sev_table = Table(sev_data, colWidths=[1.4 * inch] * 5)
    sev_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ffffff")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(sev_table)
    story.append(Spacer(1, 15))

    # ==========================================
    # 3. SCOPE & METHODOLOGY
    # ==========================================
    story.append(Paragraph("02. Scope & Defensive Methodology", section_heading))
    story.append(
        Paragraph(
            "Assessment operations strictly adhere to the 8 defensive pillars documented in the platform methodology: "
            "1) Strict Target Authorization, 2) Safe Target Discovery (GET/HEAD/OPTIONS), 3) Standard Security Checks, "
            "4) Automated Secrets Redaction, 5) Finding Classification Standard (PASS, OBSERVATION, POTENTIAL ISSUE, CONFIRMED, MANUAL), "
            "6) Conservative Severity Scoring, 7) Actionable Remediation, and 8) Audit Persistence in MySQL/TiDB.",
            body_style,
        )
    )
    story.append(Spacer(1, 15))

    # ==========================================
    # 4. SECURITY CHECKS MATRIX
    # ==========================================
    story.append(Paragraph("03. Security Checks Execution Matrix", section_heading))
    chk_table_rows = [
        [
            Paragraph("<b>Check ID</b>", body_style),
            Paragraph("<b>Title</b>", body_style),
            Paragraph("<b>Category</b>", body_style),
            Paragraph("<b>Status</b>", body_style),
            Paragraph("<b>Severity</b>", body_style),
        ]
    ]

    for c in checks:
        chk_table_rows.append(
            [
                Paragraph(f"<code>{c.check_id}</code>", body_style),
                Paragraph(f"<b>{c.title}</b>", body_style),
                Paragraph(c.category, body_style),
                Paragraph(
                    f"<font color='{'#16a34a' if c.status == 'PASS' else '#dc2626' if c.status == 'FAIL' else '#9333ea'}'><b>{c.status}</b></font>",
                    body_style,
                ),
                Paragraph(c.severity or "—", body_style),
            ]
        )

    chk_table = Table(chk_table_rows, colWidths=[1.1 * inch, 2.5 * inch, 1.5 * inch, 0.9 * inch, 1.0 * inch])
    chk_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(chk_table)
    story.append(Spacer(1, 15))

    # ==========================================
    # 5. DETAILED FINDINGS
    # ==========================================
    story.append(PageBreak())
    story.append(Paragraph("04. Vulnerability Findings & Technical Evidence", section_heading))

    if not findings:
        story.append(
            Paragraph("<i>No vulnerability findings were identified during this assessment session.</i>", body_style)
        )
    else:
        # Build evidence lookup
        evidence_by_finding: dict[int, list[Evidence]] = {}
        evidence_by_check: dict[int, list[Evidence]] = {}
        for ev in evidence_items:
            if ev.finding_id:
                evidence_by_finding.setdefault(ev.finding_id, []).append(ev)
            if ev.check_id:
                evidence_by_check.setdefault(ev.check_id, []).append(ev)

        for f in findings:
            finding_elements = []

            # Finding Header Block
            is_demo_finding = is_demo or "CONTROLLED DEMO" in f.title

            f_header_text = f"<b>{f.finding_code} — {f.title}</b>"
            finding_elements.append(
                Paragraph(
                    f_header_text,
                    ParagraphStyle(
                        "FHead",
                        parent=body_style,
                        fontName="Helvetica-Bold",
                        fontSize=11,
                        textColor=colors.HexColor("#0f172a"),
                    ),
                )
            )

            if is_demo_finding:
                finding_elements.append(
                    Paragraph(
                        "<font color='#b45309'><b>• CONTROLLED DEMONSTRATION FINDING • NOT A WORLDMONITOR FINDING</b></font>",
                        body_style,
                    )
                )
            elif f.status == "ENVIRONMENT_OBSERVATION":
                finding_elements.append(
                    Paragraph(
                        "<font color='#166534'><b>• DEVELOPMENT ENVIRONMENT OBSERVATION • NOT A CONFIRMED APPLICATION VULNERABILITY</b></font>",
                        body_style,
                    )
                )
            elif f.status == "SOURCE_REVIEW":
                finding_elements.append(
                    Paragraph(
                        "<font color='#0369a1'><b>• SOURCE CODE REVIEW OBSERVATION • DOCUMENTED MITIGATIONS ACTIVE</b></font>",
                        body_style,
                    )
                )

            # Metadata Table
            cvss_text = f"{f.cvss_score}" if f.cvss_score is not None else "CVSS score not assigned."
            f_meta = [
                [
                    Paragraph(f"<b>Severity:</b> {f.severity}", body_style),
                    Paragraph(f"<b>Status:</b> {f.status}", body_style),
                    Paragraph(f"<b>Category:</b> {f.category}", body_style),
                    Paragraph(f"<b>CVSS:</b> {cvss_text}", body_style),
                ]
            ]
            f_meta_table = Table(f_meta, colWidths=[1.75 * inch] * 4)
            f_meta_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            finding_elements.append(f_meta_table)
            finding_elements.append(Spacer(1, 4))

            # Description
            finding_elements.append(Paragraph("<b>Description:</b>", body_style))
            finding_elements.append(Paragraph(f.description or "No description recorded.", body_style))

            # Impact
            if f.impact:
                finding_elements.append(Paragraph("<b>Security & Technical Impact:</b>", body_style))
                finding_elements.append(Paragraph(f.impact, body_style))

            # Evidence
            f_ev_list = evidence_by_finding.get(f.id, [])
            if not f_ev_list and f.check_id:
                f_ev_list = evidence_by_check.get(f.check_id, [])
            if f_ev_list:
                finding_elements.append(Paragraph("<b>Technical Evidence (Sanitized):</b>", body_style))
                for ev in f_ev_list:
                    ev_text = ev.response_data or ev.request_data or "Evidence logged."
                    # Wrap long lines in evidence
                    finding_elements.append(Paragraph(ev_text.replace("\n", "<br/>"), code_style))

            # Reproduction Steps
            finding_elements.append(Paragraph("<b>Reproduction Steps:</b>", body_style))
            repro = f.reproduction_steps or "Controlled reproduction steps were not recorded."
            finding_elements.append(Paragraph(repro.replace("\n", "<br/>"), code_style))

            # Remediation
            finding_elements.append(Paragraph("<b>Defensive Remediation:</b>", body_style))
            finding_elements.append(
                Paragraph(
                    f"<font color='#166534'>{f.remediation or 'Apply standard defensive hardening.'}</font>",
                    body_style,
                )
            )
            finding_elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

            story.append(KeepTogether(finding_elements))

    # ==========================================
    # 6. MANUAL VERIFICATION, LIMITATIONS, CONCLUSION
    # ==========================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("05. Assessment Limitations & Conclusion", section_heading))
    story.append(
        Paragraph(
            "<b>Limitations:</b> Assessment scope was bounded strictly to the authorized target identifier. "
            "Automated network checks used safe, non-destructive HTTP verbs (GET, HEAD, OPTIONS). "
            "No brute-force testing or denial-of-service was performed. Automated scanning of production "
            "<code>worldmonitor.app</code> is strictly blocked by engine safety controls.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    if is_demo:
        story.append(
            Paragraph(
                "<b>Conclusion:</b> This report validates the SIH26163 assessment platform using an intentionally vulnerable "
                "local demonstration target. The findings are not evidence of vulnerabilities in World Monitor.",
                ParagraphStyle("DemoConc", parent=body_style, fontName="Helvetica-Bold", textColor=colors.HexColor("#92400e")),
            )
        )
    else:
        story.append(
            Paragraph(
                "<b>Conclusion:</b> The assessment executed successfully. All identified findings should be remediated "
                "in accordance with the defensive guidelines provided.",
                body_style,
            )
        )

    # Build PDF with NumberedCanvas for dynamic page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    return safe_filename, str(destination_path)
