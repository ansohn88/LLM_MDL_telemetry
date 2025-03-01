import json
import pandas as pd
from typing import Union

from calculate_freq_n_viz import make_freq_col, make_bar_plots_by_quantile
from utils import find_files_with_extension, deduplicate_dicts, count_genes


LYMPHOMA_DIR = "/Users/amsohn/Data/mdl_tel/endlymphoma_first_dx"
OK_DXS_FP = "/Users/amsohn/Downloads/EndLymphoma_diagnoses.xlsx"


def merge_w_ok_dxs(
        dxs_xlsx: Union[pd.DataFrame, str],
        path_reports: Union[pd.DataFrame, str]
    ) -> pd.DataFrame:
    if isinstance(dxs_xlsx, str):
        df_dxs = pd.read_excel(dxs_xlsx, engine='openpyxl', sheet_name='Sheet1')
    
    if isinstance(path_reports, str):
        with open("./lymphoma.json") as f:
            df_lymphs = pd.DataFrame(json.load(f))

    df_dxs = df_dxs.rename(columns={"MDL acc.": "ReportAccession_x"})
    df_dxs = df_dxs.astype({"MRN": "int32"})
    df_lymphs = df_lymphs.astype({"MRN": "int32"})

    df_merged = df_lymphs.merge(df_dxs, how="inner", on=["MRN", "ReportAccession_x"])

    return df_merged


MAP_LYMPHOMA_DX_CAT = {
    'A': 'Chronic lymphocytic leukemia_Small lymphocytic lymphoma (CLL_SLL)',
    'B': 'Mantle cell lymphoma (MCL)',
    'C': 'Plasma cell neoplasm (PCN)',
    'D': 'Diffuse large B-cell lymphoma (DLBCL)',
    'E': 'Lymphoplasmacytic Lymphoma (LPL)',
    'F': 'Follicular lymphoma (FL)',
    'G': 'Marginal zone lymphoma (MZL)',
    'H': 'Peripheral T-cell lymphoma (PTCL)',
    'I': 'B-cell lymphoma (BCL)',
    'J': 'Cutaneous T-cell lymphoma (CTCL)',
    'K': 'High-grade B-cell lymphoma (HGBCL)',
    'L': 'Burkitt lymphoma (BL)',
    'M': 'Myeloid sarcoma',
    'N': 'Angioimmunoblastic T-cell lymphoma (AITL)',
    'O': 'Leukemia',
    'P': 'Anaplastic large cell lymphoma (ALCL)',
    'Q': 'Hodgkins lymphoma',
    'R': 'Synchronous (more than one primary neoplasm)',
    'S': 'Dendritic_histiocytic neoplasm',
    'T': 'Negative for lymphoma'
}


def main():
    files = find_files_with_extension(
        directory=LYMPHOMA_DIR,
        extension="pkl"
    )

    list_to_df = []
    for f in files:
        df = pd.read_pickle(f)
        list_to_df.append(df)

    df = pd.DataFrame(list_to_df)
    df["dx_category"] = df["dx_category"].map(MAP_LYMPHOMA_DX_CAT)

    dx_list = df["dx_category"].unique().tolist()
# 
    df_by_dx = {}
    for dx in dx_list:
        dfdx = df.loc[df["dx_category"] == dx]
        num_of_cases = len(dfdx)
        list_of_genes = dfdx["somatic_muts"].values.tolist()
        final_log = []
        for genes in list_of_genes:
            genes = deduplicate_dicts(genes, key='gene')
            final_log.extend(genes)

        counts = count_genes(final_log)
        prepare_for_df = []
        for k, v in counts.items():
            prepare_for_df.append({'Gene': k, 'Count': v})

        dfgc = pd.DataFrame.from_dict(prepare_for_df)
        dfgc = make_freq_col(dfgc, col_to_convert='Count')

        df_by_dx[dx] = {'df_gc': dfgc, 'num_cases': num_of_cases}

    return df_by_dx


if __name__=="__main__":
    main()
    df_by_dx = main()

    out_dir = "/Users/amsohn/Programming/mdl_telemetry/outputs/lymph_first_dx"

    with pd.ExcelWriter(f'{out_dir}/endlymph_gene_freq_by_histology.xlsx') as writer:
        for histology, df_gc_nc in df_by_dx.items():
            total_gene_counts = df_gc_nc['df_gc']
            num_cases = df_gc_nc['num_cases']
            make_bar_plots_by_quantile(
                df=total_gene_counts,
                lower_quantile=0.5,
                upper_quantile=1.0,
                final_dx=histology,
                save_dir=out_dir,
                num_of_cases=num_cases
            )
            total_gene_counts.to_excel(writer, sheet_name=histology, index=False)
