import pandas as pd

def process(df_totali: pd.DataFrame, df_robot: pd.DataFrame):
    return abs(df_totali-df_robot)