
import pandas as pd

df = pd.read_csv("C:/Users/menab/OneDrive/Documentos/Projects/upwork-jobs-analyzer/upwork-jobs-analyzer/data/raw/upwork_jobs_sample.csv")
df.to_json("C:/Users/menab/OneDrive/Documentos/Projects/upwork-jobs-analyzer/upwork-jobs-analyzer/data/raw/upwork_jobs_sample.json", orient="records", indent=2)
    