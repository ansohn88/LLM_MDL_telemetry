from typing import Union
import dspy
    

class SummarizeFlowReport(dspy.Signature):
    report: str = dspy.InputField(
        desc="Flow cytometry report."
    )
    fcm_sum: str = dspy.OutputField(
        desc=f"""{low_thinking}

        Summarize the flow cytometry report in less than twenty-five words.
        """
    )


class ClassifyFlowReport(dspy.Signature):
    report: str = dspy.InputField(
        desc="Flow cytometry report."
    )
    fcm_dx: str = dspy.OutputField(
        desc=f"""{mid_thinking}
        
        ## Task Description

        Classify the pathology report into one of the following diagnostic categories:
            A) Chronic lymphocytic leukemia/Small lymphocytic lymphoma (CLL/SLL)
            B) Mantle cell lymphoma (MCL)
            C) Plasma cell neoplasm (PCN)
            D) Diffuse large B-cell lymphoma (DLBCL)
            E) Lymphoplasmacytic Lymphoma (LPL)
            F) Follicular lymphoma (FL)
            G) Marginal zone lymphoma (MZL)
            H) Peripheral T-cell lymphoma (PTCL)
            I) B-cell lymphoma (BCL)
            J) Cutaneous T-cell lymphoma (CTCL)
            K) High-grade B-cell lymphoma (HGBCL)
            L) Burkitt lymphoma (BL)
            M) Myeloid sarcoma
            N) Angioimmunoblastic T-cell lymphoma (AITL)
            O) Leukemia
            P) Anaplastic large cell lymphoma (ALCL)
            Q) Hodgkin's lymphoma
            R) Synchronous (more than one primary neoplasm)
            S) Dendritic/histiocytic neoplasm
            T) Negative for lymphoma

        Make sure to always include the final answer as only the letter of the $(diagnostic category).
        """
    )


class ExtractNGSInfo(dspy.Signature):
    report: str = dspy.InputField(
        desc="Clinical report that includes genetic variant information."
    )
    mutations: Union[None, list[dict[str, str]]] = dspy.OutputField(
        desc="""
        Your task is to extract structured data from the section titled "Variants of probable somatic origin". Ignore all other sections.

        From each row in this section, extract the following fields:
        Gene: The gene name (e.g., TP53, RUNX1, etc.)
        DNA change: The DNA change (e.g., c.3754C>A, c.86C>G, etc.)
        Protein change: The protein change (e.g., p.P1252T, p.I314T, etc.)
        VAF: The Variant Allele Frequency (e.g., 6%, <5%, etc.)
        Type: The variant type (e.g., SNV - Missense, SNV - Nonsense, etc.)

        Do not leave any of the fields blank. Return the results as a Python dictionary with the format:
        [
            {
                "Gene": "<GENE>",
                "DNA change": "<DNA_CHANGE>",
                "Protein change": "<PROTEIN_CHANGE>",
                "VAF": "<VAF>",
                "Type": "<VARIANT_TYPE>"
            },
            ...
        ]
        """
        )


class ExtractBoneMarrowDx(dspy.Signature):

    flow_context: str = dspy.InputField(
        desc="Summarized flow cytometry report."
    )
    ngs_context: list[dict] = dspy.InputField(
        desc="Molecular assay findings. If it is an empty list, that means the assay was negative for any clonal mutations."
    )
    bm_report: str = dspy.InputField(
        desc="Bone marrow pathology report with final diagnosis and clinical context under the comment."
    )
    first_dx: str = dspy.OutputField(
        desc="""
        Classify the report as one of the following:
        1) First time diagnosis (including second opinion)
        2) Relapse/refractory
        3) Follow-up

        If there is no history provided, and there is no disease detected on both the flow cytometry and the bone marrow interpretation, classify as `3) Follow-up`.
        """
    )
    history: str = dspy.OutputField(
        desc="If clinical history is provided under the comment, summarize the patient's clinical history in no more than fifty words."
    )
    pb: str = dspy.OutputField(
        desc="If ```Peripheral Blood``` is provided, summarize the peripheral blood findings in no more than twenty words. Otherwise, leave it blank."
    )
    stains: str = dspy.OutputField(
        desc="If stains (histochemical or immunohistochemical) are provided anywhere in the report, extract the contents into a dictionary with the stain name as the key and the result as the value. Including the grading/staging. " \
        "Please do NOT skip/miss any reported stains."
    )
    morphology: str = dspy.OutputField(
        desc="Summarize all the findings under ```BONE MARROW BIOPSY```, ```BONE MARROW CLOT```, and ```BONE MARROW SMEARS/TOUCH PREP``` in no more than thirty words."
    )
    cytogenetics: str = dspy.OutputField(
        desc="If there are cytogenetics findings within the report, please extract the cytogenetic abnormality. If there are none, leave it blank."
    )
    categorize: str = dspy.OutputField(
        desc="""
        ## Use the Following Reference for the Task Description Below:
        
        ### Clonal Hematopoiesis and Clonal Cytopenia of Uncertain Significance

        1. Clonal Hematopoiesis (CH):
        - Age-related condition defined by somatic variants in hematopoietic stem and progenitor cells.
        - **CHIP (Clonal Hematopoiesis of Indeterminate Potential):** Somatic mutations in genes recurrently implicated in myeloid malignancies with a minimum VAF of 2% (4% for X-linked gene mutations in males) in peripheral blood (PB).

        2. Clonal Cytopenia of Undetermined Significance (CCUS):
        - Persistent (>4 months) unexplained cytopenias (hemoglobin <13 g/dL in men and <12 g/dL in women; absolute neutrophil count <1.8 x 10^9; platelet count <150 x 10^9).
        - Demonstration of somatic pathogenic variants (minimum VAF 2%; typically at higher VAF: ≥10%-20%) or clonal chromosomal abnormalities in myeloid cells.
        - Absence of MDS diagnostic criteria (≤10% dysplastic cells of any hematopoietic cell lineage in BM and absence of excess blasts, and absence of AML-defining cytogenetic abnormalities) or other myeloid neoplasms.

        ### Myeloproliferative Neoplasms (MPNs)

        1. Chronic Myeloid Leukemia (CML):
        - Genetically defined MPN with BCR::ABL1 fusion.
        - Chronic phase: High-risk features include high ELTS score, 10%-19% myeloid blasts, >20% basophils in PB, additional chromosomal aberrations, clusters of small megakaryocytes with significant BM fibrosis.
        - Blast phase: Presence of bona fide lymphoblasts with aberrant immunophenotype by flow cytometry in PB or BM.

        2. Polycythemia Vera (PV):
        - Major criteria: Increased Hb concentration (>16.5 g/dL in men, >16.0 g/dL in women) or hematocrit (>45% in men, >48% in women), BM biopsy showing age-adjusted hypercellularity with trilineage growth, presence of JAK2 p.V617F or JAK2 exon 12 mutation.
        - Minor criterion: Subnormal serum erythropoietin level.

        3. Essential Thrombocythemia (ET):
        - Major criteria: Platelet count ≥450 x 10^9/L, BM biopsy showing proliferation mainly of the megakaryocytic lineage, WHO criteria for CML, PV, PMF, or other myeloid neoplasms not met, JAK2, CALR, or MPL mutation.
        - Minor criteria: Presence of a clonal marker or exclusion of reactive thrombocytosis.

        4. Primary Myelofibrosis (PMF):
        - **Prefibrotic stage:** Megakaryocytic proliferation and atypia without reticulin fibrosis grade >1, BM cellularity, granulocytic proliferation, and (often) decreased erythropoiesis, WHO criteria for CML, PV, ET, MDS, or other myeloid neoplasms not met, JAK2, CALR, or MPL mutation.
        - **Fibrotic stage:** Megakaryocytic proliferation and atypia with reticulin/collagen fibrosis grade 2-3, WHO criteria for CML, PV, ET, MDS, or other myeloid neoplasms not met, JAK2, CALR, or MPL mutation.

        5. Chronic Neutrophilic Leukemia (CNL):
        - WBC ≥25 x 10^9/L with neutrophils + bands ≥80% of WBC, promyelocytes, myelocytes, metamyelocytes <10% WBC, monocytes <10% WBC and <1 x 10^9/L, no dysgranulopoiesis, myeloblasts rare (<2%) in blood, hypercellular BM, neutrophils/granulocytes increased in % and number, myeloblasts <5%, exclusion of reactive neutrophilia and other WHO-defined MPN and MDS/MPN, no BCR::ABL1, PDGFRA-r, PDGFRB-r, FGFR1-r, and PCM1::JAK2 or other TKI fusions, CSF3R p.T618I or other activating CSF3R mutation.

        6. Chronic Eosinophilic Leukemia (CEL):
        - PB eosinophilia >1.5 x 10^9/L on at least 2 occasions over an interval of at least 4 weeks, evidence of clonality in myeloid lineage, abnormal BM morphology (dysplasia), WHO criteria for other myeloid or lymphoid neoplasms not met.

        7. Juvenile Myelomonocytic Leukemia (JMML):
        - Clinical, hematologic, and laboratory criteria: Peripheral blood monocyte count >1 x 10^9/L, blasts and promonocytes in PB and BM <20%, clinical evidence of organ infiltration, lack of BCR::ABL1 fusion, lack of KMT2A rearrangement.
        - Genetic criteria: Mutation in a component or a regulator of the canonical RAS pathway or noncanonical clonal RAS pathway pathogenic variant or fusions causing activation of genes upstream of the RAS pathway.
        - Other criteria: Circulating myeloid and erythroid precursors, increased hemoglobin F for age, thrombocytopenia with hypercellular marrow often with megakaryocytic hypoplasia, hypersensitivity of myeloid progenitors to GM-CSF.

        ### Myelodysplastic Neoplasms (MDS)

        1. MDS with Defining Genetic Abnormalities:
        - **MDS with Biallelic TP53 Inactivation:** <20% BM and PB blasts, often complex cytogenetics, two or more TP53 mutations, or 1 mutation with evidence of TP53 copy number loss or cnLOH.
        - **MDS with Low Blasts and SF3B1 Mutation:** <5% BM and <2% PB blasts, absence of del(5q), monosomy 7, or complex karyotype, SF3B1 mutation (VAF ≥5%).
        - **MDS with Low Blasts and del(5q):** <5% BM and <2% PB blasts, isolated del(5q) or with one additional abnormality other than monosomy 7 or del(7q), absence of biallelic TP53 aberration.

        2. MDS Defined Morphologically:
        - **MDS with Low Blasts:** <5% BM and <2% PB blasts without biallelic TP53 inactivation, SF3B1 mutation, del(5q), or other AML-defining genetic abnormalities.
        - **Hypoplastic MDS:** <5% BM and <2% PB blasts, BM cellularity <30% of normal cellularity in patients <70 years or <20% in patients ≥70 years, no clear etiology for BM hypocellularity.
        - **MDS with Increased Blasts-1 (MDS-IB1):** 5%-9% BM or 2%-4% PB blasts.
        - **MDS with Increased Blasts-2 (MDS-IB2):** 10%-19% BM or 5%-19% PB blasts, or presence of Auer rods.
        - **MDS with Fibrosis (MDS-F):** 5%-19% BM; 2%-19% PB blasts, reticulin fibrosis (grade 2 or 3).

        ### Myelodysplastic/Myeloproliferative Overlap Neoplasms

        1. Chronic Myelomonocytic Leukemia (CMML):
        - AMC ≥0.5 x 10^9/L with monocytes ≥10% of WBC differential, <20% PB and BM blasts, BM dysplasia involving ≥1 myeloid lineage seen in ≥10% of cells, presence of an acquired somatic cytogenetic or molecular abnormality, exclusion of BCR::ABL1 or myeloid/lymphoid neoplasms associated with TK fusions.

        2. MDS/MPN with Neutrophilia:
        - WBC ≥13 x 10^9/L with immature myeloid cells ≥10% of the WBC differential, prominent dysgranulopoiesis, monocytes and eosinophils comprising <10% of the differential, exclusion of BCR::ABL1, TK fusions, and MPN-associated driver mutations like JAK2, MPL, and CALR.

        3. MDS/MPN-SF3B1-T:
        - Anemia associated with dysplastic erythropoiesis and ≥15% ring sideroblasts, with or without dysplasia in the megakaryocytic and erythroid lineages, exclusion of BCR::ABL1, MPN and myeloid/lymphoid neoplasms with TK fusions, t(3;3)(q21.3;q26.2), inv(3)(q21.3q26.2), isolated del(5q), and biallelic TP53 inactivation.

        4. MDS/MPN-NOS:
        - WBC ≥13 x 10^9/L and/or the platelet count ≥450 x 10^9/L, exclusion of BCR::ABL1, myeloid/lymphoid neoplasms with TK fusions, MPN, and other MDS/MPN-overlap neoplasms, t(3;3)(q21.3;q26.2), inv(3)(q21.3q26.2), and del(5q).

        ### Acute Myeloid Leukemia (AML)

        1. AML with Defining Genetic Abnormalities:
        - **AML with gene fusions, rearrangements, or mutations (such a NPM1, CEBPA)

        2. AML Defined by Differentiation:
        - **AML with Minimal Differentiation:** <3% positivity for MPO or SBB by cytochemistry, expression of at least 2 myeloid-associated markers (MPO, CD13, CD33, and CD117).
        - **AML without Maturation:** ≥3% positivity for MPO or SBB and negative for NSF by cytochemistry, maturing cells of the granulocytic lineage constitute <10% of the nucleated BM cells, expression of 2 or more myeloid-associated antigens by flow cytometry.
        - **AML with Maturation:** ≥3% positivity for MPO or SBB by cytochemistry, maturing cells of the granulocytic lineage constitute ≥10% of the nucleated BM cells, monocyte lineage cells constitute <20% of BM cells, expression of 2 or more myeloid-associated antigens by flow cytometry.
        - **Acute Basophilic Leukemia:** Blasts and immature/mature basophils with metachromasia on toluidine blue staining, blasts are negative for MPO, SBB, and NSF, no expression of strong CD117 equivalent to mast cells.
        - **Acute Myelomonocytic Leukemia:** ≥20% monocytes and their precursors, ≥20% maturing granulocytic cells, at least 3% of the blasts should show MPO positivity.
        - **Acute Monocytic Leukemia:** ≥80% monocytes and their precursors including monoblasts and promonocytes, <20% maturing granulocytic cells, blasts and promonocytes expressing at least 2 monocytic markers including CD11c, CD14, CD36, and CD64 or NSF positivity on cytochemistry.
        - **Acute Erythroid Leukemia:** ≥30% immature erythroid cells (undifferentiated or pronormoblastic), no evidence of a significant myeloblastic component.
        - **Acute Megakaryoblastic Leukemia:** Blasts express at least one or more of the platelet glycoproteins: CD41, CD61, or CD42b.

        ### Secondary Myeloid Neoplasms

        1. Secondary Myeloid Neoplasms (sMN):
        - **Postcytotoxic Therapy:** AML, MDS, and MDS/MPN that arise following exposure to cytotoxic therapy (DNA-damaging) therapy or large-field radiation therapy for an unrelated condition.
        - **Germline Predisposition:** AML, MDS, MPN, and MDS/MPN that arise in a patient with germline predisposition to myeloid neoplasms.

        ### Mastocytosis

        1. Mastocytosis Subtypes:
        - **Systemic Mastocytosis (SM):** Multifocal dense mast cell infiltrate (≥15 mast cells) in BM and/or other extracutaneous organ(s), >25% of all mast cells have atypical morphology on BM smears or are spindle-shaped in dense and diffuse aggregates in BM biopsy or other extracutaneous organ(s), activating KIT mutation(s) at codon 816 or other KIT mutation with confirmed activating effect, expression of CD2, CD25, and/or CD30 by mast cells, baseline serum tryptase concentration >20 ng/mL in the absence of an associated myeloid neoplasm.
        - **Bone Marrow Mastocytosis:** SM criteria fulfilled, no skin lesions, no B-findings, basal serum tryptase <125 ng/mL, no dense SM infiltrates in an extramedullary site.
        - **Systemic Mastocytosis with an Associated Hematologic Neoplasm (SM-AHN):** Any subtype of SM and any type of WHO-defined myeloid neoplasm.
        - **Mast Cell Leukemia:** SM criteria fulfilled, ≥20% mast cells on BM smears, ≥10% MCs in PB (classic) and <10% mast cells in PB (aleukemic).

        ### Major Patterns of Drug-Induced Bone Marrow Changes

        1. Marrow Hypocellularity and/or Cytopenias
        - Caused by cytotoxic/cytolytic therapies, leading to myeloablation.
        - Drug-induced cytopenias can be uni-lineage or multilineage.
        - Serous fat atrophy and marrow necrosis are also observed.
        - Can mimic aplastic anemia, amyloid deposition, and marrow necrosis.
        - Marked by acellular eosinophilic stroma, scattered stromal cells, and residual lymphocytes.

        2. Marrow Hypercellularity and Cytoses
        - Induced by growth factors like G-CSF, EPO, and thrombopoietin.
        - Characterized by increased cellularity and specific morphologic changes in myeloid, erythroid, and megakaryocytic lineages.
        - Can be due to a bone marrow transplant.

        3. Maturation of Malignant Cells
        - Therapies like ATRA and IDH1/2 inhibitors induce differentiation in malignant cells.
        - This can lead to transient leukocytosis and the appearance of "intermediate cells."

        4. Dysplastic Changes
        - Various medications can cause dysmorphology in hematopoietic cells.
        - Pseudo-Pelger-Huët anomaly (PPHA) is a common finding in patients receiving immunosuppressants.

        ## Task Description

        Review the ### Summarized Flow Cytometry Report ###, ### Molecular Assay Findings ###, and ### Bone Marrow Pathology Report ### and classify into one of the diagnostic categories below.

            A) B-cell lymphoblastic leukemia / B-lymphoblastic leukemia (B-ALL)
            B) T-cell lymphoblastic leukemia / T-lymphoblastic leukemia (T-ALL)
            C) AML
            D) MPAL
            E) MDS/MPN
            F) MDS
            G) MPN
            H) Negative for disease (which includes therapy-induced dysplastic bone marrow changes)
            I) CHIP or CCUS
            J) Mastocytosis (systemic, cutaneous, mast cell sarcoma)
            K) Histiocytic neoplasms
            L) Blastic plasmacytoid dendritic cell neoplasm (BPDCN)
            M) Large granular lymphocytic leukemia (LGLL)
            N) Plasma cell neoplasm (myeloma, MGUS, lymphoplasmacytic lymphoma, Waldenstrom macroglobulinemia)
            O) Lymphoma involving bone marrow (i.e., mantle cell lymphoma, chronic lymphocytic leukemia, B-cell lymphoproliferative disorder, large B cell lymphoma, T-cell lymphoma)
            P) Anemia (i.e., aplastic anemia, red cell aplasia)
            Q) Insufficient for diagnosis
            R) Metastatic carcinoma/sarcoma/neoplasm

        Ignore any statement in the report that says to correlate with flow cytometry and molecular studies or that these two are pending--the flow cytometry and molecular studies 
        are provided separately as inputs. Use the criteria found within the Reference above to arrive at the final diagnostic category. 
        Do not include the reasoning in the final response--ONLY use the category letters.
        """
    )
    

class ExtractLymphomaReport(dspy.Signature):

    report: str = dspy.InputField(
        desc="Pathology report with final diagnosis and clinical context under the comment."
    )
    flow_context: str = dspy.InputField(
        desc="Summarized flow cytometry report."
    )
    history: str = dspy.OutputField(
        desc="If clinical history is provided under the comment, summarize the patient's clinical history in no more than 40 words."
    )
    categorize: str = dspy.OutputField(
        desc="""
        ## Task Description

        Classify the pathology report into one of the following diagnostic categories:
            A) Chronic lymphocytic leukemia/Small lymphocytic lymphoma (CLL/SLL)
            B) Mantle cell lymphoma (MCL)
            C) Plasma cell neoplasm (PCN)
            D) Diffuse large B-cell lymphoma (DLBCL)
            E) Lymphoplasmacytic Lymphoma (LPL)
            F) Follicular lymphoma (FL)
            G) Marginal zone lymphoma (MZL)
            H) Peripheral T-cell lymphoma (PTCL)
            I) B-cell lymphoma (BCL)
            J) Cutaneous T-cell lymphoma (CTCL)
            K) High-grade B-cell lymphoma (HGBCL)
            L) Burkitt lymphoma (BL)
            M) Myeloid sarcoma
            N) Angioimmunoblastic T-cell lymphoma (AITL)
            O) Leukemia
            P) Anaplastic large cell lymphoma (ALCL)
            Q) Hodgkin's lymphoma
            R) Synchronous (more than one primary neoplasm)
            S) Dendritic/histiocytic neoplasm
            T) Negative for lymphoma

        Make sure to always include the final answer as only the letter of the $(diagnostic category).
        """
    )
