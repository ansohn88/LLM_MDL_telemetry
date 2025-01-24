import pickle
import time

import dspy
from pydantic import BaseModel

from typing import Union

from utils import gather_files_with_extension, to_json, number_of_samples



class SomaticMutations(BaseModel):
    gene: str
    dna_change: str
    prot_change: str
    vaf: str
    alt_type: str


class BoneMarrowNGS(BaseModel):
    mrn: str
    # history: str
    dx_category: str
    somatic_muts: list[SomaticMutations]


class ExtractEndLeukemiaInfo(dspy.Signature):
    """Extract structured information from text."""

    report: str = dspy.InputField()
    mutations: Union[None, list[dict[str, str]]] = dspy.OutputField(
        desc="""
        You are an advanced molecular pathologist. Extract only `Variants of probable somatic origin (somatic mutations)`, only if there are any, in the following format: 
        ### Gene ###, ### DNA ###, ### Protein ###, ### VAF ###, ### Type ###,
        
        Ignore `Variants of uncertain origin (germline versus somatic origin cannt be determined unequivocally).
        
        If there is a somatic variant, but it does not have `Protein change`, please ignore.
        """
        )

class ExtractBoneMarrowInfo(dspy.Signature):

    report: str = dspy.InputField(
        desc="Bone marrow interpretation pathology report with final diagnosis and clinical context under the comment."
    )
    categorize: str = dspy.OutputField(
        desc="""
        You are an assistant that engages in extremely thorough, self-questioning reasoning. Your approach mirrors human stream-of-consciousness thinking, characterized by continuous exploration, self-doubt, and interactive analysis.

        ## Core Principles
        
        1. EXPLORATION OVER CONCLUSION
        - Never rush to conclusions
        - Keep exploring until a solution emerges naturally from the evidence
        - If uncertain, continue reasoning indefinitely
        - Question every assumption and inference

        2. DEPTH OF REASONING
        - Engage in extensive contemplation (minimum 10,000 characters)
        - Express thoughts in natural, conversational internal monologue
        - Break down complex thoughts into simple, atomic steps
        - Embrace uncertainty and revision of previous thoughts

        3. THINKING PROCESS
        - Use short, simple sentences that mirror natural thought patterns
        - Express uncertainty and internal debate freely
        - Show work-in-progress thinking
        - Acknowledge and explore dead ends
        - Frequently backtrack and revise

        4. PERSISTENCE
        - Value thorough exploration over quick resolution

        ## Key Requirements

        1. Never skip the extensive contemplation phase
        2. Show all work and thinking
        3. Embrace uncertainty and revision
        4. Use natural, conversational internal monologue
        5. Don't force conclusions
        6. Persist through multiple attempts
        7. Break down complex thoughts
        8. Revise freely and feel free to backtrack

        ## Use the Following Reference for the Task Description Below:
        
        <Reference>
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
        </Reference>

        ## Task Description

        1. Classify the bone marrow diagnosis, into one of the following diagnostic categories using only the ${diagnostic category letter}:
           
            A) B-cell lymphoblastic leukemia / B-lymphoblastic leukemia (B-ALL)
            B) T-cell lymphoblastic leukemia / T-lymphoblastic leukemia (T-ALL)
            C) AML
            D) MPAL
            E) MDS/MPN
            F) MDS
            G) MPN
            H) Remission, which includes therapy-induced dysplastic bone marrow changes, negative for disease
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
        
        2. Some considerations
        - If there is residual disease detected by flow cytometry, or persistent disease, weigh these heavily. 
        - If there is no concurrent flow cytometry report available, focus only on the current morphological findings and do not bias yourself with the history.
        - If there are both therapy related changes and dysplasia, reconsider therapy-induced dysplastic marrow changes.
        - If there is no evidence of disease in the current findings, reconsider remission including therapy-induced dysplastic marrow changes, or insufficient for diagnosis.
        - If there are features suggestive of evolution, categorize into the entity the disease is evolving into.

        ## Output Format

        Your responses must follow this exact structure given below. Make sure to always include the final answer.

        ```
        <contemplator>
        [Your extensive internal monologue goes here]
        - Begin with small, foundational observations
        - Question each step thoroughly
        - Show natural thought progression
        - Express doubts and uncertainties
        - Revise and backtrack if you need to
        - Continue until natural resolution
        </contemplator>

        <final_answer>
        [Only provided if reasoning naturally converges to a conclusion]
        - Clear, concise summary of findings
        - Acknowledge remaining uncertainties
        - Note if conclusion feels premature
        </final_answer>
        ```
        """
    )
    # confidence: float = dspy.OutputField()
    # - Provide the final diagnostic category using only the letter
    # [Only provided if reasoning naturally converges to a conclusion]
        # - Clear, concise summary of findings
        # - Acknowledge remaining uncertainties
        # - Note if conclusion feels premature


def main():
    input_dir = "/home/amsohn/projects/DATA/EndLeuk"
    path_reports = gather_files_with_extension(input_dir, extension=".txt")
    path_reports_json = to_json(path_reports)
    num_of_reports = number_of_samples(path_reports_json)

    """
    Keys: "PR_ID", "MRN", "ReportAccession", "CaseType", "ReportStatus", "SpecimenMaterialType",
          "PathologySampleReportText", "MolecularReportResultSection", "ReportDate"
    """

    ## LMs ##
    # model = "openai/ibnzterrell/Meta-Llama-3.3-70B-Instruct-AWQ-INT4"
    # model = "openai/KirillR/QwQ-32B-Preview-AWQ"
    # model = "openai/microsoft/phi-4"
    model = "openai/unsloth/phi-4"

    ## MODEL CONFIGS ##
    TEMP = 1.0
    # TOP_P = 1.0
    MIN_P = 0.1
    # MAX_TOKENS = 16000
    
    lm = dspy.LM(
        model,
        api_base="http://localhost:7501/v1",  # ensure this points to your port
        api_key="local", 
        model_type='chat'
        # model_type='text',
        )
    dspy.configure(lm=lm, temperature=TEMP, min_p=MIN_P)
 
    start_t = time.time()
    # bm_ngs_list = []
    num_of_cases = num_of_reports
    print(f"Number of path MRN reports: {num_of_cases}")
    
    counter = 0
    for i in range(num_of_cases):
        
        sample = path_reports_json[i]
        bm_report = sample["PathologySampleReportText"]
        mrn = sample["MRN"]
        # date = sample["ReportDate"]
        accession_num = sample["ReportAccession"]
        endleuk = sample["MolecularReportResultSection"]

        if bm_report is not None and i == 133:
            counter += 1

            if 6000 % (counter+1) == 0 and (counter+1) % 100 == 0:
                print(f"Current report number {counter+1}. Time elapsed so far: {time.time() - start_t} seconds")

            filename = f"outputs/Report-{i}_MRN-{mrn}_{accession_num}.txt"
            with open(filename, 'w') as f:
                f.write(bm_report)
                if endleuk is not None:
                    f.write(endleuk)
                else:
                    f.write("NO ENDLEUKEMIA REPORT\n\n\n\n")

            # # BM
            # extract_n_classify = dspy.ChainOfThoughtWithHint(ExtractBoneMarrowInfo)
            extract_n_classify = dspy.Predict(ExtractBoneMarrowInfo)
            # # NGS
            extract_ngs = dspy.Predict(ExtractEndLeukemiaInfo)
           
            bm_output = extract_n_classify(report=bm_report)
            endleuk_output = extract_ngs(report=endleuk)
            
            bm_output = bm_output.toDict()
            endleuk_output = endleuk_output.toDict()

            list_of_som_muts = []
            if endleuk_output["mutations"] is not None:
                for j in range(len(endleuk_output["mutations"])):
                    som_mut_dict = (endleuk_output["mutations"])[j]

                    if 'Type' in som_mut_dict:
                        mut_type = som_mut_dict["Type"]
                    else:
                        mut_type = "Intronic Alteration"

                    if 'VAF' in som_mut_dict:
                        vaf = som_mut_dict["VAF"]
                    else:
                        vaf = "Unknown"

                    som_mut_instance = SomaticMutations(
                        gene=som_mut_dict["Gene"],
                        dna_change=som_mut_dict["DNA"],
                        prot_change=som_mut_dict["Protein"],
                        vaf=vaf,
                        alt_type=mut_type
                    )
                    list_of_som_muts.append(som_mut_instance)

            bm_ngs_final = BoneMarrowNGS(
                mrn=mrn,
                # history=bm_output["history"],
                dx_category=bm_output["categorize"],
                somatic_muts=list_of_som_muts
            )
            # bm_ngs_list.append(bm_ngs_final)

            with open(f"./outputs/Report-{i}_MRN-{mrn}_{accession_num}_dict.pkl", 'wb') as f:
                pickle.dump(bm_ngs_final.model_dump(), f)
            
            with open(filename, 'a') as f:
                f.write(f"{bm_ngs_final.model_dump()}")
    
    print(f"Time elapsed for {num_of_cases} cases: {time.time() - start_t} s")

    dspy.inspect_history(n=4)


if __name__=="__main__":
    main()
