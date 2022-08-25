import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def model(what):
    base = full_model[full_model['Substitution'] == 'None'][
        [what, 'Group type', 'Type', 'Substitution']]

    # Substitution part
    sub_model = full_model.copy()
    sub_model = sub_model[[what, 'Group type', 'Type', 'Substitution']]
    to_ster = sub_model.copy()
    sub_model = sub_model.merge(base, on=['Type', 'Group type'], suffixes=['', '_base'], how='left')
    sub_model.drop(columns=['Substitution_base'], inplace=True)
    sub_model['Difference'] = sub_model[what] - sub_model[what + '_base']
    sub_model_done = sub_model.groupby('Substitution').mean()
    sub_model_done.drop(columns=[what, what + '_base'], inplace=True)
    sub_model_done.iloc[[0, 3, 4, 7, 8, 11], 0] = sub_model_done.iloc[[2, 1, 6, 5, 10, 9], 0]
    sub_model_done.drop(index='None', inplace=True)

    # Sterical part
    ster_model = to_ster.merge(base, on=['Type', 'Group type'], suffixes=['', '_base'], how='left')
    ster_model.drop(columns=['Substitution_base'], inplace=True)
    ster_model = ster_model.merge(sub_model_done, on='Substitution', suffixes=['', '_sub'], how='left')
    ster_model['Difference ster'] = sub_model[what] - sub_model[what + '_base'] - \
                                    ster_model['Difference']
    ster_model = ster_model.groupby('Substitution').mean()
    ster_model_done = ster_model.drop(columns=[what, what + '_base', 'Difference'])
    ster_model_done.drop(index='None', inplace=True)

    return base, sub_model_done, ster_model_done


full_model_para = pd.read_csv('model_full_para.csv', index_col=0, header=0)
full_model_para['Type'] = 'para'
full_model_meta = pd.read_csv('model_full_meta.csv', index_col=0, header=0)
full_model_meta['Type'] = 'meta'
full_model = pd.concat([full_model_para, full_model_meta])
full_model['Substitution'] = full_model.index
full_model.sort_values(['Substitution', 'Type'], inplace=True)

full_model_orto = pd.read_csv('model_full_orto.csv', index_col=0, header=0)
full_model_orto['Type'] = 'orto'

baseE, subE, sterE = model('Act. Ene. [kcal/mol]')
baseS, subS, sterS = model('Sec. Min. [kcal/mol]')

'''full_model = pd.concat([full_model, full_model_orto])
full_model['Substitution'] = full_model.index
full_model.sort_values(['Substitution', 'Type'], inplace=True)
baseE, sub_dont, ster_dont = model('Act. Ene. [kcal/mol]')
baseS, sub_dont, ster_dont = model('Sec. Min. [kcal/mol]')'''

# Model tester
tester = full_model.copy()
tester = tester[['Act. Ene. [kcal/mol]', 'Group type', 'Type', 'Substitution']]
tester = tester.merge(baseE, on=['Type', 'Group type'], suffixes=['', '_base'], how='left')
tester.drop(columns=['Substitution_base'], inplace=True)
tester = tester.merge(subE, on='Substitution', suffixes=['', '_sub'], how='left')
tester = tester.merge(sterE, on='Substitution', suffixes=['', '_sub'], how='left')
tester['Theoretical Activation Energy'] = tester['Act. Ene. [kcal/mol]_base'] + tester['Difference'] + tester['Difference ster']
tester['Precision'] = tester['Act. Ene. [kcal/mol]'] - tester['Theoretical Activation Energy']
tester['% Precision'] = (tester['Precision'] / tester['Act. Ene. [kcal/mol]'])*100
tester.set_index('Substitution', drop=False, inplace=True)
tester.drop(index='None', inplace=True)

testerS = full_model.copy()
testerS = testerS[['Sec. Min. [kcal/mol]', 'Group type', 'Type', 'Substitution']]
testerS = testerS.merge(baseS, on=['Type', 'Group type'], suffixes=['', '_base'], how='left')
testerS.drop(columns=['Substitution_base'], inplace=True)
testerS = testerS.merge(subS, on='Substitution', suffixes=['', '_sub'], how='left')
testerS = testerS.merge(sterS, on='Substitution', suffixes=['', '_sub'], how='left')
testerS['Theoretical Second Minimum'] = testerS['Sec. Min. [kcal/mol]_base'] + testerS['Difference'] + testerS['Difference ster']
testerS['Precision'] = testerS['Sec. Min. [kcal/mol]'] - testerS['Theoretical Second Minimum']
testerS['% Precision'] = (testerS['Precision'] / testerS['Sec. Min. [kcal/mol]'])*100
testerS.set_index('Substitution', drop=False, inplace=True)
testerS.drop(index='None', inplace=True)

# New comp test
test_files = pd.read_csv('test.csv', index_col=0, header=0)
base_test = test_files.loc['None', :]
test = test_files.copy()
test.drop(index='None', inplace=True)
test['Substitution'] = test.index
test['Base AE'] = base_test['Activation energy']
test = test.merge(subE, on='Substitution', how='left')
test = test.merge(sterE, on='Substitution', how='left')
test['Theoretical AE'] = test['Base AE'] + test['Difference'] + test['Difference ster']
test['Precision AE'] = test['Activation energy'] - test['Theoretical AE']
test['% Precision AE'] = (test['Precision AE'] / test['Activation energy'])*100
test['Base SM'] = base_test['Second minimum']
test = test.merge(subS, on='Substitution', how='left', suffixes=['', '_SM'])
test = test.merge(sterS, on='Substitution', how='left', suffixes=['', '_SM'])
test['Theoretical SM'] = test['Base SM'] + test['Difference_SM'] + test['Difference ster_SM']
test['Precision SM'] = test['Second minimum'] - test['Theoretical SM']
test['% Precision SM'] = (test['Precision SM'] / test['Second minimum'])*100

# New doublecomp test
test_files2 = pd.read_csv('test_double.csv', header=0, delimiter="\t")
base_test2 = test_files2.iloc[0, :]

test2 = test_files2.copy()
test2.drop(index=0, inplace=True)
test2['Base AE'] = base_test2['Activation energy']
test2 = test2.merge(subE, left_on='Substituent 1', right_on='Substitution', how='left')
test2 = test2.merge(subE, left_on='Substituent 2', right_on='Substitution', how='left', suffixes=[' 1', ' 2'])
test2 = test2.merge(sterE, left_on='Substituent 1', right_on='Substitution', how='left')
test2 = test2.merge(sterE, left_on='Substituent 2', right_on='Substitution', how='left', suffixes=[' 1', ' 2'])
test2['Theoretical AE'] = test2['Base AE'] + test2['Difference 1'] + test2['Difference ster 1'] + test2['Difference 2'] + test2['Difference ster 2']
test2['Precision AE'] = test2['Activation energy'] - test2['Theoretical AE']
test2['% Precision AE'] = (test2['Precision AE'] / test2['Activation energy'])*100



test2['Base SM'] = base_test2['Second minimum']



plt.style.use('ggplot')

fig2, axes = plt.subplots(2, 2, figsize=(15, 10))

fig2.suptitle('Model performance', fontsize=20)

sns.swarmplot(x='Substitution', y='Act. Ene. [kcal/mol]', ax=axes[0, 0], data=tester, color='b', size=3, alpha=0.5)
sns.swarmplot(x='Substitution', y='Theoretical Activation Energy', ax=axes[0, 0], data=tester, color='r', size=3, alpha=0.5)
axes[0, 0].set_title('Activation energy - base group')
axes[0, 0].set_xlabel('')
axes[0, 0].set_ylabel('Activation Energy [kcal/mol]')
axes[0, 0].set_xticklabels(axes[0, 0].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
axes[0, 0].set_ylim(5, 10)

sns.swarmplot(x='Substitution', y='Sec. Min. [kcal/mol]', ax=axes[1, 0], data=testerS, color='b', size=3, alpha=0.5)
sns.swarmplot(x='Substitution', y='Theoretical Second Minimum', ax=axes[1, 0], data=testerS, color='r', size=3, alpha=0.5)
axes[1, 0].set_title('Second minimum - base group')
axes[1, 0].set_ylabel('Second minimum [kcal/mol]')
axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
axes[1, 0].set_ylim(3.5, 7.5)

sns.swarmplot(x='Substitution', y='Activation energy', ax=axes[0, 1], data=test, color='b', size=10, alpha=0.5)
sns.swarmplot(x='Substitution', y='Theoretical AE', ax=axes[0, 1], data=test, color='r', size=10, alpha=0.5)
axes[0, 1].set_title('Activation energy - test group')
axes[0, 1].set_xlabel('')
axes[0, 1].set_ylabel('Activation Energy [kcal/mol]')
axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
axes[0, 1].set_ylim(5, 10)

sns.swarmplot(x='Substitution', y='Second minimum', ax=axes[1, 1], data=test, color='b', size=10, alpha=0.5)
sns.swarmplot(x='Substitution', y='Theoretical SM', ax=axes[1, 1], data=test, color='r', size=10, alpha=0.5)
axes[1, 1].set_title('Second minimum - test group')
axes[1, 1].set_ylabel('Second minimum [kcal/mol]')
axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
axes[1, 1].set_ylim(3.5, 7.5)

plt.subplots_adjust(hspace=0.32)
#plt.show()
fig2.savefig("model.png")

fig1, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.swarmplot(x='Substitution', y='% Precision', ax=axes[0], data=tester, color='g', size=3, alpha=0.5)
sns.swarmplot(x='Substitution', y='% Precision', ax=axes[0], data=testerS, color='y', size=3, alpha=0.5)
axes[0].set_title('Residuals - base group')
axes[0].set_ylabel('Residuals [kcal/mol]')
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
axes[0].set_ylim(-10, 10)

sns.swarmplot(x='Substitution', y='% Precision AE', ax=axes[1], data=test, color='g', size=10, alpha=0.5)
sns.swarmplot(x='Substitution', y='% Precision SM', ax=axes[1], data=test, color='y', size=10, alpha=0.5)
axes[1].set_title('Residuals - test group')
axes[1].set_ylabel('Residuals [kcal/mol]')
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
axes[1].set_ylim(-10, 10)
fig1.savefig("model_residuals.png")
plt.show()
print('done')