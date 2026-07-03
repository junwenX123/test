# Reanalysis without Bonferroni correction

This report removes Bonferroni correction from the previous diagnostic analysis. The inferential column is now the original one-sided exact binomial p-value for T-zone enrichment, compared directly with 0.05. The Bonferroni-adjusted p-values and Bonferroni alpha are not used.

## Statistical rule used after correction removal

For each pre-specified parameter setting, let $K_T$ be the number of analyzed deaths in the fixed T-zone and let $n$ be the number of analyzed deaths. The null model is spatial uniformity:

$$H_0: \pi_T=p_0=|T|/|W|=0.4444,\qquad H_A:\pi_T>p_0.$$

The p-value is the one-sided exact binomial tail probability

$$p=\mathbb P_{H_0}(K_T\ge k_T),\qquad K_T\sim \operatorname{Binomial}(n,p_0).$$

Decision rule in this revised analysis: report enrichment when the raw one-sided binomial p-value is below $0.05$. Because the simulations are diagnostic and mechanism-oriented, the main evidence is not a multiple-comparison discovery claim but the stability of effect sizes across replicates, parameter regimes, and two observation designs.

## Experiment 1A: fixed 1000 analyzed deaths

Result after removing Bonferroni: all 15 death/ERK parameter settings remain significant at raw p < 0.05. The pooled T-zone fraction is always above the geometric null p0 = 0.4444.

| erk_regime            |   n_settings |   n_significant_p005 |   min_fraction |   mean_fraction |   max_fraction |   min_density_ratio |   mean_density_ratio |   max_density_ratio |   max_p_value |
|:----------------------|-------------:|---------------------:|---------------:|----------------:|---------------:|--------------------:|---------------------:|--------------------:|--------------:|
| reference_ERK         |            5 |                    5 |          0.622 |           0.632 |          0.642 |               2.056 |                2.148 |               2.246 |     5.21e-278 |
| strong_ERK_protection |            5 |                    5 |          0.559 |           0.589 |          0.608 |               1.584 |                1.795 |               1.941 |     1.2e-116  |
| weak_ERK_protection   |            5 |                    5 |          0.617 |           0.643 |          0.658 |               2.015 |                2.257 |               2.409 |     3.44e-263 |

Interpretation: lambda_d mainly changes the time required to collect 1000 analyzed deaths. The strongest Spearman correlations are between lambda_d and analysis time: strong ERK rho=-0.966, reference ERK rho=-0.974, weak ERK rho=-0.980. The T-zone enrichment remains present for every lambda_d.


## Experiment 1B: fixed physical-time control

Result after removing Bonferroni: all 15 fixed-time settings remain significant at raw p < 0.05. Therefore the enrichment is not created only by the fixed-1000-death stopping rule.

| erk_regime            |   n_settings |   n_significant_p005 |   min_fraction |   mean_fraction |   max_fraction |   min_density_ratio |   mean_density_ratio |   max_density_ratio |   max_p_value |
|:----------------------|-------------:|---------------------:|---------------:|----------------:|---------------:|--------------------:|---------------------:|--------------------:|--------------:|
| reference_ERK         |            5 |                    5 |          0.607 |           0.629 |          0.649 |               1.929 |                2.128 |               2.309 |     1.97e-134 |
| strong_ERK_protection |            5 |                    5 |          0.579 |           0.588 |          0.608 |               1.718 |                1.789 |               1.937 |     2.93e-47  |
| weak_ERK_protection   |            5 |                    5 |          0.639 |           0.647 |          0.658 |               2.215 |                2.291 |               2.406 |     3.26e-171 |

Interpretation: under a fixed physical window, increasing lambda_d strongly increases the number of observed deaths. Spearman rho(lambda_d, number of deaths) is 0.944 for strong ERK, 0.977 for reference ERK, and 0.980 for weak ERK. But the T-zone fraction remains systematically above p0.


## Experiment 2: activation localization × death/ERK robustness

Result after removing Bonferroni: medium and local activation still show enrichment in all 15 settings each. Non-local activation shows 0/15 settings significant even without Bonferroni. This is the decisive result.

| activation_regime    |   beta_a_R |   beta_a_T |   n_settings |   n_significant_p005 |   min_fraction |   mean_fraction |   max_fraction |   min_density_ratio |   mean_density_ratio |   max_density_ratio |   max_p_value |
|:---------------------|-----------:|-----------:|-------------:|---------------------:|---------------:|----------------:|---------------:|--------------------:|---------------------:|--------------------:|--------------:|
| local_activation     |        5   |        3   |           15 |                   15 |          0.895 |           0.907 |          0.914 |              10.655 |               12.211 |              13.218 |      0        |
| medium_activation    |        2.5 |        3   |           15 |                   15 |          0.569 |           0.622 |          0.657 |               1.648 |                2.071 |               2.399 |      7.1e-137 |
| non_local_activation |        1   |        1.2 |           15 |                    0 |          0.387 |           0.424 |          0.447 |               0.787 |                0.921 |               1.012 |      1        |

Interpretation: removing Bonferroni does not change the mechanistic conclusion. Non-local activation remains non-enriched, medium activation remains clearly enriched, and local activation remains extremely enriched. Therefore activation localization is still the dominant mechanism controlling the existence of T-zone enrichment.


## Revised final conclusion

After removing Bonferroni correction, the conclusions are essentially unchanged, but the wording should be changed. Do not write “significant after Bonferroni correction.” Instead write “significant according to the raw one-sided exact binomial test at level 0.05.”

Across Experiments 1A and 1B, every tested death/ERK setting remains enriched. In Experiment 2, non-local activation remains not enriched even without correction, while medium and local activation are enriched in all tested settings. Thus the main mechanism is activation localization; lambda_d mainly controls temporal speed; ERK feedback modulates enrichment strength.
