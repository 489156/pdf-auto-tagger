# ESG PDF Auto-Tagger & Auditor — Workflow & Architecture Blueprint

## 1. Executive Summary
- **Positioning**: Automated sustainability disclosure validator that maps 100+ page corporate ESG reports to GRI 2021, IFRS S1/S2, and TCFD standards, generating standardized Content Index Excel spreadsheets in 3 minutes.
- **Target Personas**: ESG disclosure managers at publicly listed companies, sustainability report consulting agencies, ESG rating analysts.

## 2. Click-Level Functional Workflow
1. **Upload & Framework Selection**:
   - Upload PDF Sustainability Report (up to 150+ pages).
   - Check target frameworks (`GRI 2021`, `IFRS S1/S2 Climate`, `TCFD`).
2. **Automated Indicator Mapping**:
   - Background vector similarity and regex extraction map text/table blocks to standardized ESG indicators.
   - Calculates indicator disclosure completeness (%) and detects missing clauses (e.g. biogenic CO2 breakdown under GRI 305-1).
3. **Split-View Verification Workbench**:
   - Left side: Highlighted PDF snippet with exact page number tracking.
   - Right side: Indicator metadata, extracted quantitative values, and 1-click `[Approve and Include in Index]` button.
4. **1-Click Standardized Excel Export**:
   - Generates production-ready GRI Content Index (`.xlsx`) with clickable page references and color-coded compliance status.

## 3. Deployment Flow (Cloudflare Pages)
1. Push this repository to GitHub `main`.
2. Connect to Cloudflare Pages (Build preset: None / Static HTML).
3. Set root directory to `prototype/` (or move `index.html` to root).
