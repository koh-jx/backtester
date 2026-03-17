import pandas as pd

def export_dataframe_to_csv(df, filename):
    df.to_csv(filename, index=False)

def export_and_open_csv(df, filename):
    export_dataframe_to_csv(df, filename)
    import os
    os.startfile(filename)
    