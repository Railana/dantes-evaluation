#!/usr/bin/env python3

import sys
import os
import pandas as pd

columns = ['Mystery Guest',	
'Test Code Duplication',
'Unknown Test',
'Test Run War',
'EmptyTest',
'Verbose Test',
'Default Test',
'Resource Optimism',
'Exception Catching Throwing',
'Print Statement',
'Assertion Roulette',
'Eager Test',
'Sleepy Test',
'Dependent Test',
'Redundant Assertion',
'Magic Number Test',
'Conditional Test Logic',
'For Test Only',
'General Fixture',	
'IgnoredTest',
'Sensitive Equality',	
'Duplicate Assert',
'Indirect Test',
'Constructor Initialization',
'Lazy Test']

def read_jnose_csv(filename):
    return pd.read_csv(filename, sep=';', usecols=columns)

def main(test_smells_before_file, after_dantes_file):

    df_before = read_jnose_csv(test_smells_before_file)
    df_after = read_jnose_csv(after_dantes_file)

    df_diff = pd.DataFrame({
        'Test Smell': columns,
        'Before Dantes': df_before.sum(),
        'After Dantes': df_after.sum(),
        'Difference (%)': (df_before.sum() - df_after.sum())/df_before.sum() * 100
    })

    df_diff['Difference (%)'] = df_diff['Difference (%)'].fillna(0)
    df_diff['Difference (%)'] = df_diff['Difference (%)'].round(2)
    df_diff = df_diff.sort_values(by='Difference (%)', ascending=False)

    print(df_diff)

    result_file = os.path.join(os.path.dirname(test_smells_before_file), 'test_smells_comparison.csv')
    df_diff.to_csv(result_file, index=False)

if __name__ == "__main__":
    test_smells_before_file = sys.argv[1]
    after_dantes_file = sys.argv[2]
    main(test_smells_before_file, after_dantes_file)
