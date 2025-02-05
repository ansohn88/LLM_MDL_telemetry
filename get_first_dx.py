from datetime import datetime
import json


"""
Column/keys of the provided EPIC views:

[
    'PR_ID', 'MRN', 'ReportDate_x', 'ReportAccession_x', 'CaseType_x', 'ReportStatus', 
    'SpecimenMaterialType', 'SpecimenCollectionDate', 'MolecularReportResultSection', 
    'MolecularReportText', 'PathologySampleAccession','PathologySampleReportText', 'ID',
    'ReportDate_y', 'ReportAccession_y', 'CaseType_y', 'Component', 'Intepretation', 'CombinedReport'
]
"""


PATH_REPORTS_FILEPATH = ""


def convert_to_datetime(date_string):
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")


def return_matching_dict(d, desired_k, desired_v):
    return {
        k: v for k, v in d.items() if k == desired_k and v == desired_v
    }


def deduplicate_by_mrn(all_reports):
    by_mrn = {}
    for report in all_reports:
        key = report["MRN"]
        value = {"MRN": key,
                 "SpecimenCollectionDate": report["SpecimenCollectionDate"],
                 "MolecularReportResultSection": report["MolecularReportResultSection"],
                 "PathologySampleReportText": report["PathologySampleReportText"],
                 "FlowComponent": report["Component"],
                 "FlowInterpretation": report["Intepretation"],
                 "CombinedReport": report["CombinedReport"]}
        if key not in by_mrn:
            by_mrn[key] = []
        by_mrn[key].append(value)

    return by_mrn


def sort_by_collection_dates(reports_by_mrn, save_as_json):
    sorted_list = sorted(
        reports_by_mrn, key = lambda x: convert_to_datetime(x["SpecimenCollectionDate"])
    )
    return sorted_list


def filter_by_first_dx(reports_by_mrn):
    original_dx = []
    for _, v in reports_by_mrn.items():
        if len(v) == 1:
            original_dx.append(v)
        else:
            sorted_reports = sort_by_collection_dates(v)
            original_dx.append(sorted_reports[0])

    if save_as_json:
        with open(FINAL_REPORTS_FILEPATH, 'w') as json_file:
            json_file.write(json.dumps(original_dx))

    return original_dx


def main():
    with open(PATH_REPORTS_FILEPATH) as f:
        leukemia = json.load(f)

    by_mrn = deduplicate_by_mrn(leukemia)
    first_dxs = filter_by_first_dx(by_mrn)
    assert len(by_mrn) == len(first_dxs)


if __name__=='__main__':
    main()
