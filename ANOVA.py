from scipy import stats
from data_clean import *
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
'''方差齐性检验'''

data_clean = data_clean()
jobs = data_clean.get_all()
# 数据处理
jobs = jobs.drop(jobs.loc[jobs['exp'].isnull()].index)
jobs = jobs.drop(jobs.loc[jobs['edu'].isnull()].index)
jobs = jobs.drop(jobs.loc[jobs['place'].isnull()].index)
jobs['low_salary'] = jobs['low_salary'].round(0)

formula = 'low_salary~edu+exp'  #公式
datas = jobs[['edu', 'exp', 'low_salary']]  # 数据
anova_results = anova_lm(ols(formula,datas).fit())
# anova_lm:多因素方差分析
print(anova_results)

'''说明：检验结果中，两个因素的P值都小于0.5，拒绝原假设，说明学历和经验对薪资有显著差异'''