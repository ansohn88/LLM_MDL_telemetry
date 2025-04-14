import pandas as pd

from calculate_freq_n_viz import make_freq_col, make_bar_plots_by_quantile
from utils import find_files_with_extension, deduplicate_dicts, count_genes


MAP_DX_CATEGORY = {
    "A": "B_ALL",
    "B": "T_ALL",
    "C": "AML",
    "D": "MPAL",
    "E": "MDS_MPN",
    "F": "MDS",
    "G": "MPN",
    "H": "Negative_for_disease",
    "I": "CHIP_CCUS",
    "J": "Mastocytosis",
    "K": "Histiocytic_neoplasms",
    "L": "BPDCN",
    "M": "T_LGLL",
    "N": "Plasma_cell_neoplasm",
    "O": "Lymphoma",
    "P": "Anemia",
    "Q": "Insufficient_for_diagnosis",
    "R": "Metastatic_solid_tumor"
}


def main():
    files = find_files_with_extension(
        directory="/Users/amsohn/Data/mdl_tel/endleukemia_first_dx/",
        extension="pkl"
    )

    list_to_df = []
    for f in files:
        df = pd.read_pickle(f)
        list_to_df.append(df)

    df = pd.DataFrame(list_to_df)
    
    df["dx_category"] = df["dx_category"].replace("C) AML", "C")
    df["dx_category"] = df["dx_category"].map(MAP_DX_CATEGORY)
    df = df[df['dx_category'].notna()]

    dx_list = df["dx_category"].unique().tolist()

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
    df_by_dx = main()

    out_dir = "/Users/amsohn/Programming/mdl_telemetry/outputs/leuk_first_dx"

    with pd.ExcelWriter(f'{out_dir}/endleuk_gene_freq_by_histology.xlsx') as writer:
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
