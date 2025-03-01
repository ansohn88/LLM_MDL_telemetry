from collections import Counter
from typing import Union, Optional

import altair as alt
import pandas as pd

from utils import find_files_with_extension


INPUT_DIR = "/Users/amsohn/Programming/mdl_telemetry/cleaned_data/by_final_diagnosis"
INPUT_DIR_FOR_BAR_CHARTS = "/Users/amsohn/Programming/mdl_telemetry/outputs/mapp_final_dx"
OUTPUT_DIR = "/Users/amsohn/Programming/mdl_telemetry/outputs/final_dx"


def make_gene_freq_df_from_finaldx(
        df: pd.DataFrame, 
    ) -> Union[None, pd.DataFrame]:

    df = df.groupby(by=["MU_MACCESSION"])
    num_of_cases = int(len(df))

    mdl_gene_list_agg = []
    for name, group in df:
        gene_list = group["MU_GENE"].unique()
        mdl_gene_list_agg.append(gene_list)

    running_count = Counter()
    for gene_list in mdl_gene_list_agg:
        running_count.update(gene_list)

    to_df = []
    for k, v in running_count.items():
        to_df.append({'Gene': k, 'Count': v})
    
    return {
        'df': pd.DataFrame(to_df),
        'num_of_cases': num_of_cases
    }


def make_mapp_gene_count(
        input_dir: str,
        col_to_freq: str
    ) -> dict[str, pd.DataFrame]:
    csv_files = find_files_with_extension(
        directory=input_dir,
        extension='csv'
    )

    gene_counts_by_finaldx = {}
    for csv in csv_files:
        fname = csv.stem
        df = pd.read_csv(csv, sep='\t')
        num_cases = len(df['MU_MACCESSION'].unique())
        df_gene_counts = make_gene_freq_df_from_finaldx(df)

        if df_gene_counts['num_of_cases'] >= 5:
            df_to_process = df_gene_counts['df']
            df_to_process = make_freq_col(df_to_process, col_to_freq)
            df_to_process.to_csv(f'{INPUT_DIR_FOR_BAR_CHARTS}/{fname}.csv', sep='\t', index=False)
            gene_counts_by_finaldx[fname] = {'df_gc': df_to_process, 'num_cases': num_cases}
        else:
            print(f'{fname} has *less than* (<) 5 cases!')

    return gene_counts_by_finaldx


def make_freq_col(
        df: pd.DataFrame, 
        col_to_convert: str
    ) -> pd.DataFrame:

    total = df[col_to_convert].sum()
    df["Frequency"] = df.apply(
        lambda row: (row[col_to_convert] / total) * 100.,
        axis=1
    )
    df = df.sort_values(by="Frequency", ascending=False)
    return df


def make_bar_plots_by_quantile(
        df: pd.DataFrame,
        lower_quantile: float,
        upper_quantile: float,
        final_dx: str,
        save_dir: str,
        num_of_cases: Optional[int]
    ) -> None:

    df["Count"] = df["Count"].astype(int)
    lower_bound = df["Count"].quantile(lower_quantile)
    upper_bound = df["Count"].quantile(upper_quantile)

    df = df.loc[
        (df["Count"] >= lower_bound) & (df["Count"] <= upper_bound)
    ]

    if num_of_cases is not None:
        title = alt.TitleParams(f'{final_dx} (Case#: {num_of_cases})', anchor='middle')
    else:
        title = alt.TitleParams(f'Diagnosis: {final_dx}', anchor='middle')
    
    chart = alt.Chart(df, title=title).mark_bar().encode(
        x='Gene',
        y='Frequency',
    )
    chart.save(f"{save_dir}/{final_dx}.png", 
               ppi=400)


if __name__=="__main__":
    all_gene_counts = make_mapp_gene_count(INPUT_DIR, col_to_freq='Count')
    
    with pd.ExcelWriter('./mapp_gene_freq_by_histology.xlsx') as writer:
        for histology, df_gc_nc in all_gene_counts.items():
            total_gene_counts = df_gc_nc['df_gc']
            num_cases = df_gc_nc['num_cases']
            make_bar_plots_by_quantile(
                df=total_gene_counts,
                lower_quantile=0.8,
                upper_quantile=1.,
                final_dx=histology,
                save_dir=INPUT_DIR_FOR_BAR_CHARTS,
                num_of_cases=num_cases
            )
            total_gene_counts.to_excel(writer, sheet_name=histology, index=False)


    # for histology, df_gc_nc in all_gene_counts.items():
    #     print(f'{histology}: {df_gc_nc['num_cases']}')
