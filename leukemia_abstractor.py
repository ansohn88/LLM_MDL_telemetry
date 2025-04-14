import json
import pickle
import time

import dspy

from utils import number_of_samples, search_listdict_by_keys
from hemepath_signatures import ExtractBoneMarrowDx, SummarizeFlowReport, ExtractNGSInfo
from hemepath_dataclasses import SomaticMutations, HemepathResults


def main():
    # Load the bone marrow and NGS reports
    leukemia_json_filepath = "/home/amsohn/projects/DATA/telemetry/leukemia.json"
    with open(leukemia_json_filepath) as f:
        path_reports_json = json.load(f)
    num_of_reports = number_of_samples(path_reports_json)

    # Load the flow cytometry reports
    fcm_filepath = "/home/amsohn/projects/DATA/telemetry/all_fcms_filtered.json"
    with open(fcm_filepath) as f:
        all_fcm = json.load(f)

    ## LM models ##
    # model = "openai/JamAndTeaStudios/DeepSeek-R1-Distill-Qwen-32B-FP8-Dynamic"
    model = "openai/deepcogito/cogito-v1-preview-qwen-14B"

    ## LM configs ##
    TEMP = 0.6
    TOP_P = 0.95
    MIN_P = 0.01
    MAX_TOKENS = 48000
    
    ## Init LM
    lm = dspy.LM(
        model,
        api_base="http://localhost:7501/v1",  # ensure this points to your port
        api_key="local", 
        model_type='chat'
        )
    dspy.configure(lm=lm, temperature=TEMP, min_p=MIN_P, top_p=TOP_P, max_tokens=MAX_TOKENS)
 
    start_t = time.time()
    num_of_cases = num_of_reports
    print(f"Number of path MRN reports: {num_of_cases}")
    
    counter = 0
    for i in range(num_of_cases):

        sample = path_reports_json[i]
        bm_report = sample["PathologySampleReportText"]
        endleuk = sample["MolecularReportResultSection"]
        mrn = sample["MRN"]
        collection_date = sample["SpecimenCollectionDate"]

        if bm_report is not None:
            counter += 1

            if 6000 % (counter+1) == 0 and (counter+1) % 100 == 0:
                print(f"Current report number {counter+1}. Time elapsed so far: {time.time() - start_t} seconds")

            filename = f"/home/amsohn/projects/tel_sglang2/outputs_leukemia_first_extra/Report-{i}_MRN-{mrn}_{collection_date}.txt"

            # # LM Predictors
            flow_summarizer = dspy.Predict(SummarizeFlowReport)
            extract_n_classify = dspy.Predict(ExtractBoneMarrowDx)
            extract_ngs = dspy.Predict(ExtractNGSInfo)

            # Retrieve flow cytometetry intepretation
            fcm_interp = search_listdict_by_keys(
                list_of_dicts=all_fcm,
                keys_to_search=["MRN", "SpecimenCollectionDate"],
                values_to_match=[mrn, collection_date]
            )
            fcm_sum = flow_summarizer(report=fcm_interp).fcm_sum

            # Extract somatic mutations from NGS report
            endleuk_output = extract_ngs(report=endleuk).mutations

            print(endleuk_output)

            list_of_som_muts = []
            if endleuk_output is not None:
                for som_mut_dict in endleuk_output:
                    if 'VAF' in som_mut_dict:
                        vaf = som_mut_dict["VAF"]
                    else:
                        vaf = "Unknown"

                    # print(som_mut_dict)
                    som_mut_instance = SomaticMutations(
                        gene=som_mut_dict["Gene"],
                        dna_change=som_mut_dict["DNA change"],
                        prot_change=som_mut_dict["Protein change"],
                        vaf=vaf,
                        alt_type=som_mut_dict["Type"]
                    )
                    list_of_som_muts.append(som_mut_instance)

            # Categorize BM report + flow summary
            bm_dx_cat = extract_n_classify(
                flow_context=fcm_sum,
                ngs_context=endleuk_output,
                bm_report=bm_report
            ).toDict()
           
            # Only categorize first time diagnoses
            report_type = bm_dx_cat["first_dx"]
            if report_type == "1) First time diagnosis (including second opinion)":

                # Write BM and NGS reports (for visualization)
                with open(filename, 'w') as f:
                    f.write(bm_report)
                    if endleuk is not None:
                        f.write("\n\n\n\nENDLEUKEMIA EXTRACT\n")
                        f.write(endleuk)
                    else:
                        f.write("NO ENDLEUKEMIA REPORT\n\n\n\n")

                # Organize all results into dataclass
                bm_ngs_final = HemepathResults(
                    mrn=mrn,
                    report_type=report_type,
                    fcm=fcm_sum,
                    history=bm_dx_cat["history"],
                    dx_category=bm_dx_cat["categorize"],
                    pb=bm_dx_cat["pb"],
                    stains=bm_dx_cat["stains"],
                    morphology=bm_dx_cat["morphology"],
                    cytogenetics=bm_dx_cat["cytogenetics"],
                    somatic_muts=list_of_som_muts
                )

                # Save organized results
                with open(f"/home/amsohn/projects/tel_sglang2/outputs_leukemia_first_extra/Report-{i}_MRN-{mrn}_{collection_date}_dict.pkl", 'wb') as f:
                    pickle.dump(bm_ngs_final.model_dump(), f)
                
                with open(filename, 'a') as f:
                    f.write(f"{bm_ngs_final.model_dump()}")
    
    print(f"Time elapsed for {num_of_cases} cases: {time.time() - start_t} s")

    # dspy.inspect_history(n=16)


if __name__=="__main__":
    main()
