import numpy as np
import pandas as pd

data = pd.read_csv('../project.csv')
se_ages = pd.Series(data["size"])
x =  pd.Series([1,2,3,4,5])
bins = [
    0, 100,1000,10000, 100000, 1000000, 10000000
]
se1 = pd.cut(se_ages,bins)
print(pd.value_counts(se1))
