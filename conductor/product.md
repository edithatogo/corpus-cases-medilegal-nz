# Initial Concept

Within this folder - "C:/Users/60217257/OneDrive - Flinders/repos/legal-nz" - is a series of related projects to parliament and legal documents and nlp for nz. 

I want to create corpus from public findings and cases, beginning with HDC: "https://www.hdc.org.nz/decisions/search-decisions/", then "https://www.hpdt.org.nz/Search-Decisions", then to these: https://www.justice.govt.nz/tribunals/, https://www.era.govt.nz/, https://www.teachersdisciplinarytribunal.nz/. 

I'll want to upload each corpus to hugging face, github and zenodo, similar to what has been done for: "C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\corpus-law-nz" and "C:\Users\60217257\OneDrive -Flinders\repos\legal-nz\corpus-cases-medilegal-nz". 

Initially we don't need to extract anything from them. Start by just transferring the raw data/files, then we will progressively manage them, for instance, with OCR. 

I'm trying to build a shared library in "C:\Users\60217257\OneDrive - Flinders\repos\legal-nz\nlp-policy-nz" for all processing scripts, with the data kept separately. 

This is the hugging face site: https://huggingface.co/edithatogo. 

You may need to consider how we organise Hugging Face, as the number of datasets expands. 

I think if you look within the other repo's, you'll find I've already started to develop some conventions, so you could leverage that work. 

Those repos are also on github already: https://github.com/edithatogo/corpus-legislation-nz, https://github.com/edithatogo/nlp-policy-nz, https://github.com/edithatogo/corpus-nz-hansard. 

Try to systematise all of this work. 

I do also want it to be bleeding edge though.

---

# Product Guide: New Zealand Legal and Medical-Legal Corpora

## 1. Product Vision & Goal
The goal of this project is to create a bleeding-edge, systematic, and open-source corpus collection from New Zealand public findings and legal/medical-legal case decisions. The project aims to consolidate raw data and progressive processing workflows (such as OCR) into a unified, clean, and easily queryable format. 

By separating data from processing logic, the data resides in individual repositories (e.g., `corpus-cases-medilegal-nz`), while all shared extraction, processing, and NLP scripts are maintained in a central shared library (`nlp-policy-nz`).

## 2. Target Users & Use Cases
The corpus is designed for:
*   **NLP Researchers and Practitioners:** For training and fine-tuning large language models (LLMs) on domain-specific New Zealand legal and medical-legal text.
*   **Legal & Medical-Legal Professionals:** For legal case analysis, precedent tracking, decision research, and compliance monitoring.
*   **Policy Makers & Government Agencies:** For analyzing regulatory trends and outcomes across different NZ tribunals.
*   **The General Public & Domain Enthusiasts:** Anyone interested in open-access legal data in New Zealand.

## 3. Scope of Data Sources
The corpus will be compiled sequentially, beginning with medical-legal sources and expanding to broader tribunals:
1.  **Health and Disability Commissioner (HDC):** Decisions search (https://www.hdc.org.nz/decisions/search-decisions/)
2.  **Health Practitioners Disciplinary Tribunal (HPDT):** Search decisions (https://www.hpdt.org.nz/Search-Decisions)
3.  **Ministry of Justice Tribunals:** (https://www.justice.govt.nz/tribunals/)
4.  **Employment Relations Authority (ERA):** (https://www.era.govt.nz/)
5.  **Teachers Disciplinary Tribunal:** (https://www.teachersdisciplinarytribunal.nz/)

## 4. Key Features & Delivery Channels
*   **Raw File Transfer (Initial Phase):** Establish pipelines to fetch and store raw PDF/HTML files systematically without text extraction.
*   **Progressive Processing:** Incrementally build out pipeline steps such as OCR, text cleanup, metadata extraction, and structuring.
*   **Multi-Platform Distribution:** Upload each completed corpus to:
    *   **Hugging Face:** (https://huggingface.co/edithatogo) under a structured organization naming convention.
    *   **GitHub:** For open-source code and metadata tracking.
    *   **Zenodo:** For long-term archival and DOI assignment.
*   **Shared Code Infrastructure:** Integrate all processing and ingestion logic into the `nlp-policy-nz` shared library to keep individual corpus repos clean and focused on data.
