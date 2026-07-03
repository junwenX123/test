# Pooled T-zone binomial test without Bonferroni correction

## Method

For each parameter setting, the five independent replicates were pooled. Each replicate contributes 1000 analyzed observed deaths after a burn-in of 500 observed deaths, so the pooled sample size is N = 5 × 1000 = 5000 for each parameter setting.

The pooled number of T-zone deaths was tested against the geometric null probability p0 = |T|/|W| = 4/9 ≈ 0.4444 using a one-sided exact binomial test:

$$H_0:\pi=p_0,\qquad H_A:\pi>p_0.$$

Following the supervisor's correction, no Bonferroni correction is applied. The decision rule is the nominal per-parameter rule p < 0.05. Therefore the columns `bonferroni_alpha`, `bonferroni_adjusted_p_value`, and `significant_after_bonferroni_0p05` should be removed from the report.

The pooled T-zone density ratio is

$$\rho_T=\frac{K/p_0}{(N-K)/(1-p_0)}.$$

## Main numerical conclusions

- Number of parameter settings tested: 52.
- Number of settings significant at the nominal 0.05 level: 34/52.
- Compared with the old Bonferroni table, exactly one additional setting becomes significant: `T1e-1_c1e-4_ratio_1e3_betaR2p5_betaT2p0` (K/N = 2286/5000, fraction = 0.4572, p = 0.0359, density ratio = 1.053). This should be described as weak or borderline evidence, not as a strong localization effect.

## Key settings

| parameter setting | replicates | pooled k/n | pooled fraction | density ratio | pooled one-sided p-value | nominal p<0.05? | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| `baseline` | 5 | 2187/5000 | 0.4374 | 0.972 | 0.8453 | No | no evidence of enrichment |
| `higher_death_rate` | 5 | 2219/5000 | 0.4438 | 0.997 | 0.542 | No | no evidence of enrichment |
| `larger_ERK_radius` | 5 | 2084/5000 | 0.4168 | 0.893 | 1 | No | no evidence of enrichment |
| `shorter_ERK_duration` | 5 | 2205/5000 | 0.4410 | 0.986 | 0.6929 | No | no evidence of enrichment |
| `stronger_T_zone_activation` | 5 | 2107/5000 | 0.4214 | 0.910 | 0.9995 | No | no evidence of enrichment |
| `T0p5_c0p005_ratio_1e2` | 5 | 2210/5000 | 0.4420 | 0.990 | 0.6412 | No | no evidence of enrichment |
| `T0p5_c0p0005_ratio_1e3` | 5 | 2119/5000 | 0.4238 | 0.919 | 0.9984 | No | no evidence of enrichment |
| `T0p5_c0p00005_ratio_1e4` | 5 | 2119/5000 | 0.4238 | 0.919 | 0.9984 | No | no evidence of enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR2p5_betaT2p0` | 5 | 2286/5000 | 0.4572 | 1.053 | 0.03595 | Yes | nominal enrichment |
| `T0p5_c0p005_ratio_1e2_local_activation` | 5 | 4525/5000 | 0.9050 | 11.908 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p0005_ratio_1e3_local_activation` | 5 | 4548/5000 | 0.9096 | 12.577 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_local_activation` | 5 | 4661/5000 | 0.9322 | 17.187 | 0 (below machine precision) | Yes | very strong enrichment |

## Full pooled results

| parameter setting | replicates | pooled k/n | pooled fraction | density ratio | pooled one-sided p-value | nominal p<0.05? | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| `strong_visible_T_zone` | 5 | 4525/5000 | 0.9050 | 11.908 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_local_activation` | 5 | 4525/5000 | 0.9050 | 11.908 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p0005_ratio_1e3_local_activation` | 5 | 4548/5000 | 0.9096 | 12.577 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_local_activation` | 5 | 4661/5000 | 0.9322 | 17.187 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR2p5_betaT5p0` | 5 | 3848/5000 | 0.7696 | 4.175 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR3p5_betaT2p0` | 5 | 3865/5000 | 0.7730 | 4.257 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR3p5_betaT3p0` | 5 | 4161/5000 | 0.8322 | 6.199 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR3p5_betaT5p0` | 5 | 4328/5000 | 0.8656 | 8.051 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR5p0_betaT1p2` | 5 | 4340/5000 | 0.8680 | 8.220 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR5p0_betaT2p0` | 5 | 4498/5000 | 0.8996 | 11.200 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR5p0_betaT3p0` | 5 | 4525/5000 | 0.9050 | 11.908 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR5p0_betaT5p0` | 5 | 4566/5000 | 0.9132 | 13.151 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR7p5_betaT1p2` | 5 | 4662/5000 | 0.9324 | 17.241 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR7p5_betaT2p0` | 5 | 4658/5000 | 0.9316 | 17.025 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR7p5_betaT3p0` | 5 | 4738/5000 | 0.9476 | 22.605 | 0 (below machine precision) | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR7p5_betaT5p0` | 5 | 4725/5000 | 0.9450 | 21.477 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR2p5_betaT5p0` | 5 | 3908/5000 | 0.7816 | 4.473 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR3p5_betaT2p0` | 5 | 4043/5000 | 0.8086 | 5.281 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR3p5_betaT3p0` | 5 | 4297/5000 | 0.8594 | 7.640 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR3p5_betaT5p0` | 5 | 4429/5000 | 0.8858 | 9.696 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR5p0_betaT1p2` | 5 | 4398/5000 | 0.8796 | 9.132 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR5p0_betaT2p0` | 5 | 4518/5000 | 0.9036 | 11.717 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR5p0_betaT3p0` | 5 | 4661/5000 | 0.9322 | 17.187 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR5p0_betaT5p0` | 5 | 4627/5000 | 0.9254 | 15.506 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR7p5_betaT1p2` | 5 | 4725/5000 | 0.9450 | 21.477 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR7p5_betaT2p0` | 5 | 4720/5000 | 0.9440 | 21.071 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR7p5_betaT3p0` | 5 | 4743/5000 | 0.9486 | 23.069 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR7p5_betaT5p0` | 5 | 4749/5000 | 0.9498 | 23.650 | 0 (below machine precision) | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR2p5_betaT3p0` | 5 | 3252/5000 | 0.6504 | 2.326 | 1.503e-188 | Yes | very strong enrichment |
| `T0p5_c0p005_ratio_1e2_betaR2p5_betaT3p0` | 5 | 3165/5000 | 0.6330 | 2.156 | 4.477e-158 | Yes | very strong enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR3p5_betaT1p2` | 5 | 2541/5000 | 0.5082 | 1.292 | 8.735e-20 | Yes | nominal enrichment |
| `T0p5_c0p005_ratio_1e2_betaR3p5_betaT1p2` | 5 | 2532/5000 | 0.5064 | 1.282 | 8.674e-19 | Yes | nominal enrichment |
| `T0p5_c0p005_ratio_1e2_betaR2p5_betaT2p0` | 5 | 2435/5000 | 0.4870 | 1.187 | 8.378e-10 | Yes | nominal enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR2p5_betaT2p0` | 5 | 2286/5000 | 0.4572 | 1.053 | 0.03595 | Yes | nominal enrichment |
| `higher_death_rate` | 5 | 2219/5000 | 0.4438 | 0.997 | 0.542 | No | no evidence of enrichment |
| `T0p5_c0p005_ratio_1e2` | 5 | 2210/5000 | 0.4420 | 0.990 | 0.6412 | No | no evidence of enrichment |
| `T0p5_c0p005_ratio_1e2_betaR2p5_betaT1p2` | 5 | 2210/5000 | 0.4420 | 0.990 | 0.6412 | No | no evidence of enrichment |
| `shorter_ERK_duration` | 5 | 2205/5000 | 0.4410 | 0.986 | 0.6929 | No | no evidence of enrichment |
| `baseline` | 5 | 2187/5000 | 0.4374 | 0.972 | 0.8453 | No | no evidence of enrichment |
| `T0p5_c0p01_ratio_50` | 5 | 2179/5000 | 0.4358 | 0.966 | 0.8934 | No | no evidence of enrichment |
| `T0p5_c0p025_ratio_20` | 5 | 2172/5000 | 0.4344 | 0.960 | 0.9257 | No | no evidence of enrichment |
| `T1e-2_c1e-3_ratio_1e1` | 5 | 2153/5000 | 0.4306 | 0.945 | 0.9765 | No | no evidence of enrichment |
| `T1e-1_c1e-3_ratio_1e2` | 5 | 2142/5000 | 0.4284 | 0.937 | 0.9893 | No | no evidence of enrichment |
| `T1e-1_c1e-4_ratio_1e3` | 5 | 2142/5000 | 0.4284 | 0.937 | 0.9893 | No | no evidence of enrichment |
| `T1e-1_c1e-4_ratio_1e3_betaR2p5_betaT1p2` | 5 | 2142/5000 | 0.4284 | 0.937 | 0.9893 | No | no evidence of enrichment |
| `T1e-1_c1e-2_ratio_1e1` | 5 | 2135/5000 | 0.4270 | 0.932 | 0.9938 | No | no evidence of enrichment |
| `T0p5_c0p0005_ratio_1e3` | 5 | 2119/5000 | 0.4238 | 0.919 | 0.9984 | No | no evidence of enrichment |
| `T0p5_c0p00005_ratio_1e4` | 5 | 2119/5000 | 0.4238 | 0.919 | 0.9984 | No | no evidence of enrichment |
| `T1e-2_c1e-4_ratio_1e2` | 5 | 2119/5000 | 0.4238 | 0.919 | 0.9984 | No | no evidence of enrichment |
| `T1e-3_c1e-4_ratio_1e1` | 5 | 2113/5000 | 0.4226 | 0.915 | 0.9991 | No | no evidence of enrichment |
| `stronger_T_zone_activation` | 5 | 2107/5000 | 0.4214 | 0.910 | 0.9995 | No | no evidence of enrichment |
| `larger_ERK_radius` | 5 | 2084/5000 | 0.4168 | 0.893 | 1 | No | no evidence of enrichment |

## Revised interpretation

The baseline setting still does not show T-zone enrichment: the pooled fraction is 0.4374, which is below p0 = 0.4444, and the one-sided p-value is 0.845. The main control scenarios also remain non-significant: higher death rate, larger ERK radius, shorter ERK duration, and stronger T-zone activation are all compatible with the spatially uniform null model with respect to the T-zone indicator.

Increasing the T-zone/outside activation contrast alone is still not sufficient. For example, the ratio-100 setting `T0p5_c0p005_ratio_1e2` gives fraction 0.4420 and p = 0.641; the ratio-1000 and ratio-10000 settings give fraction 0.4238 and p = 0.998. Thus the absence of Bonferroni correction does not change this conclusion.

The strong conclusion remains the localization mechanism: when activation is spatially localized and/or short-lived, the T-zone fraction becomes much larger than the null area fraction. For example, local activation settings have pooled fractions around 0.9050–0.9322 and density ratios about 11.9–17.2. The beta_R/beta_T sweep shows the same transition: increasing beta_R, which reduces the mean activation radius, and increasing beta_T, which shortens the activation lifetime, makes the T-zone signal much stronger.

