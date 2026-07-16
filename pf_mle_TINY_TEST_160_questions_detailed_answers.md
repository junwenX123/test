# pf_mle_caspase_erk_TINY_TEST：160 个问题详细回答

对应代码：pf_mle_caspase_erk_TINY_TEST(4).py。  
说明：严格保留用户的 1–160 编号。重复问题仍回答，并指出相互关系。

# 第一部分：Python、模型标题和运行配置（1–40）

## 1. Python 的 None 是什么意思？

**None** 表示“没有值”“目前没有对象”或“此选项未提供”。它是 Python 的一个特殊单例对象，类型是 NoneType；它不同于：

- 数字 0；
- 布尔值 False；
- 空字符串 ""；
- 空列表 []。

例如：

    x = None
    print(x is None)   # True

在本代码中：

    TARGET_DEATHS = None

不是说目标死亡数为 0，而是说“没有设置目标死亡数”，所以模拟不按死亡数量停止。

又如：

    area_points: np.ndarray | None = None

表示调用者可以提供一个 NumPy 数组，也可以不提供。若是 None，函数就在内部生成积分点。

判断 None 推荐用：

    x is None

而不是 x == None，因为 None 表示对象身份上的特殊单例。

## 2. “观测驱动的 caspase–ERK 点过程模型的粒子滤波极大似然”是什么意思？

可以逐词拆开：

1. **caspase–ERK 模型**：模型包含隐藏的 caspase 激活区域 \(V_t^a\)、观测死亡 \(V_t^d\) 和隐藏 ERK 保护区域 \(V_t^p\)。
2. **点过程模型**：数据不是规则时间表上的连续数值，而是一系列带时间、空间位置的事件 \((x_k,y_k,s_k)\)。
3. **观测驱动**：一次观测死亡不仅提供信息，还会触发一个新的 ERK 保护区。因此未来状态转移受已经观测到的死亡历史驱动。
4. **粒子滤波**：由于 \(V_t^a,V_t^p\) 看不见且积分无法解析计算，用许多随机隐藏路径“粒子”近似条件分布。
5. **极大似然**：对每组参数 \(\theta\) 计算近似似然 \(\widehat L(\theta)\)，寻找使它最大的参数：

\[
\widehat\theta=\arg\max_\theta \widehat L(\theta).
\]

所以整句话的白话含义是：

> 用许多模拟的隐藏 caspase/ERK 路径，近似解释已经观察到的死亡事件的概率，然后寻找最能解释这些死亡数据的模型参数。

## 3. 为什么硬指示函数容易让所有粒子权重接近 0？soft 模式有什么用？

硬模型的死亡强度为：

\[
\lambda^d(x,t)
=\lambda_d
\mathbf1\{x\in A(V_t^a)\}
\mathbf1\{x\notin A(V_t^p)\}.
\]

对某个观测死亡位置 \(x_k\)：

- 若粒子的 active 圆盘恰好覆盖 \(x_k\)，且 ERK 不覆盖，事件强度是 \(\lambda_d\)；
- 否则事件强度严格为 0。

bootstrap 粒子是从隐藏状态的先验转移中随机传播的，没有提前“瞄准”死亡位置。若死亡发生在 \((4.2,7.1)\)，20 个粒子的随机 active 圆盘可能都没盖住这个精确位置。于是所有粒子在这一死亡上的事件似然都为 0：

\[
G_k^{(1)}=\cdots=G_k^{(20)}=0.
\]

更新后：

\[
\widetilde w_k^{(i)}=w_{k-1}^{(i)}G_k^{(i)}=0,
\]

无法归一化，这叫**权重坍塌**。

soft 模式把硬 0/1 换成连续值。例如圆半径 \(r=1\)，死亡点距圆心 \(d=1.05\)，\(\sigma=0.1\)：

\[
\text{hard}=0,\qquad
\text{soft}=\operatorname{sigmoid}((1-1.05)/0.1)
=\operatorname{sigmoid}(-0.5)\approx0.378.
\]

该粒子仍获得较小但非零的支持，缓解全体坍塌。

## 4. 为什么不把 \(X_t=(V_t^a,V_t^p)\) 当作自主 HMM，而要增广为 \(Z_t=(V_t^a,V_t^p,V_{0:t}^d)\)？

标准“自主”隐藏马尔可夫模型要求：

\[
P(X_{t+\Delta}\mid X_{0:t},Y_{0:t})
=P(X_{t+\Delta}\mid X_t).
\]

即知道当前隐藏状态 \(X_t\) 后，未来隐藏状态不再需要过去观测。

但本模型中，观测死亡会触发 ERK：

1. 在 \(s_k-\) 时刻先发生死亡；
2. 在死亡位置 \(x_k\) 生成隐藏 ERK 半径 \(R_{E,k}\)；
3. 这个 ERK 区域影响以后死亡。

所以状态传播需要知道“现在是否出现了一次观测死亡、死亡在哪”。转移实际上是：

\[
P(V_{t+\Delta}^a,V_{t+\Delta}^p
\mid V_t^a,V_t^p,V_{0:t}^d).
\]

若只写 \(X_t=(V_t^a,V_t^p)\)，却又在代码中使用死亡历史触发新 ERK，那么 \(X_t\) 不是一个不受外部观测影响的自主链。

一种严谨写法是把共同观测历史一起放进增广状态：

\[
Z_t=(V_t^a,V_t^p,V_{0:t}^d).
\]

这样“未来只依赖当前增广状态”，恢复马尔可夫性。

但是代码没必要让每个粒子重复保存同一份 \(V_{0:t}^d\)，因为死亡数据对全部粒子都相同。代码只保存各粒子不同的 \(V_t^a,V_t^p\)，把死亡序列作为共同外部输入。这也可以称为**条件于观测的受控/观测驱动状态空间模型**。

还有一个细节：如果当前 \(V_t^p\) 完整包含所有仍有效保护区，而且寿命指数分布具有无记忆性，那么当前 \(V_t^p\) 可能已经概括了过去死亡对未来的部分影响；但在联合过程的严格描述和事件触发顺序上，显式包含死亡历史最清楚。

## 5. “Simulate synthetic death-event data from the original Gillespie model”翻译和解释

翻译：

> 使用原始 Gillespie 模型模拟合成的死亡事件数据。

解释：

- **simulate**：用随机数按模型规律生成一次可能的实验；
- **synthetic data**：人造数据，不是真实显微实验数据；
- **death-event data**：每个数据点是 \((x,y,t)\)，表示死亡位置和时间；
- **original Gillespie model**：用原始硬 0/1 模型和连续时间随机跳跃算法生成。

先人为指定真参数，例如 \(\lambda_{a,T}=0.5\)，模拟出死亡数据，再只把死亡数据交给推断器，检查能否估回 0.5。这叫参数恢复实验或 simulation study。

Gillespie 算法根据当前所有事件率：

1. 抽下一事件等待时间；
2. 抽事件类别；
3. 更新状态；
4. 重复。

## 6. bootstrap 粒子滤波权重坍塌那段英文的翻译和解释

翻译：

> bootstrap 粒子滤波器可能出现严重的权重坍塌，因为随机模拟出的隐藏激活区域通常不会覆盖观测死亡发生的精确位置。为了调试和推断，本脚本提供 LIKELIHOOD_MODE="soft"，它是硬指示函数的平滑近似。如果希望使用模型的字面原始形式，请设置 LIKELIHOOD_MODE="exact"。

解释：

bootstrap PF 的提议分布就是隐藏状态转移分布：

\[
q(z_k\mid z_{k-1},Y_k)
=p(z_k\mid z_{k-1}),
\]

它没有利用当前死亡 \(Y_k\) 来引导粒子。因此死亡信息很尖锐时，大多数粒子与观测不匹配。

“exact”表示尽量按原始硬模型：

\[
\mathbf1\{x\in A\}\in\{0,1\}.
\]

“soft”用 sigmoid 给边界附近连续分数。但本代码 exact 仍用 \(10^{-12}\) 替代真正的 0，所以它在数值上也不是百分之百严格的原模型。

## 7. dependencies 是什么意思？

dependencies 翻译为**依赖项**或**依赖库**。

代码本身使用了其他软件包提供的功能：

- NumPy：数组、随机数、数学运算；
- SciPy：差分进化和 L-BFGS-B 优化。

如果电脑没安装 SciPy，导入就失败。依赖项相当于“这个程序运行前必须具备的外部工具”。

## 8. scipy.optimize 是什么？

SciPy 是 Python 科学计算库；scipy.optimize 是其中负责优化、求根、最小二乘等任务的子模块。代码：

    from scipy.optimize import differential_evolution, minimize

表示只从 scipy.optimize 导入两个函数：

- differential_evolution：有边界的随机种群全局搜索；
- minimize：统一的局部最小化接口，这里 method="L-BFGS-B"。

SciPy 的接口基本都是“最小化”。若要最大化 \(\ell(\theta)\)，通常最小化：

\[
f(\theta)=-\ell(\theta).
\]

## 9. differential_evolution：全局随机优化是什么意思？

**差分进化**同时维护多组候选参数，不只从一个点沿梯度走。

假设候选向量为 \(\theta_1,\ldots,\theta_S\)。算法会：

1. 随机选择若干种群成员；
2. 用它们的差构造变异向量，例如

\[
v=\theta_{\mathrm{best}}+F(\theta_a-\theta_b);
\]

3. 与原候选交叉产生试验向量；
4. 若试验向量目标函数更小，就替换原候选；
5. 重复多代。

“全局”不代表数学上保证找到绝对全局最优，而是它在整个边界范围维持多个搜索点，比单起点局部优化更能跳出局部极小值。

“随机”表示初始种群、变异和交叉含随机数；固定 seed 才能复现。

## 10. minimize：局部最小化、可选 L-BFGS-B 是什么意思？

minimize 从一个给定初始点 best_x 开始，在附近寻找更低目标值。

L-BFGS-B：

- L：limited-memory，有限内存；
- BFGS：一种拟牛顿法，用历史梯度变化近似曲率；
- B：支持 box bounds，即每个参数有上下界。

它速度通常比全局随机搜索快，但依赖局部形状和初始点，可能停在局部最优。代码先用差分进化粗略全局搜索，再可选用 L-BFGS-B 在最好点附近“抛光”。

## 11. except Exception as exc 和 raise ... from exc

原代码：

    try:
        from scipy.optimize import differential_evolution, minimize
    except Exception as exc:
        raise ImportError("This script needs scipy: pip install scipy") from exc

逐步解释：

1. try：尝试导入；
2. 若导入过程中出现 Exception，进入 except；
3. as exc：把原始异常对象保存到变量 exc；
4. raise ImportError(...)：抛出更容易理解的新错误；
5. from exc：把新错误与原错误串联，回溯中能看到根本原因；
6. pragma: no cover：告诉代码覆盖率工具不用要求测试这个异常分支，不影响实际运行。

更严格的写法通常捕获 ImportError，而不是过宽的 Exception，因为后者可能掩盖 SciPy 内部的其他异常。

## 12. 为什么 20 个粒子太少？

粒子滤波用有限个样本近似一个复杂的隐藏路径分布。一般 Monte Carlo 误差随 \(N\) 大约按 \(1/\sqrt N\) 下降，但常数可能很大，而且多个死亡区间会累积退化。

20 个粒子的问题：

- 最大 ESS 也只有 20；
- 一个强观测后可能只有 1–3 个粒子获得主要权重；
- 重采样会复制少数路径，隐藏状态多样性迅速丢失；
- 对数似然随 PF seed 波动很大；
- 优化器可能追逐随机噪声。

从 20 增到 80，理想情况下标准误差约减半；增到 320 才再减半。正式所需 N 没有统一值，应比较 N=50、100、200、500 时的似然标准差和参数稳定性。

## 13. 50 个固定均匀点近似面积是什么意思？

目标面积是：

\[
|D_t|,\qquad
D_t=A(V_t^a)\setminus A(V_t^p).
\]

圆盘可能重叠并被 ERK 挖掉，解析面积很麻烦。于是从整个窗口 \(W\) 均匀抽 \(M=50\) 个点 \(U_m\)，计算其中多少落在 \(D_t\)：

\[
\widehat{|D_t|}
=|W|\frac1M\sum_{m=1}^{M}\mathbf1\{U_m\in D_t\}.
\]

例：\(W\) 面积为 100，50 点中 12 点激活且未保护，则估计面积：

\[
100\times12/50=24.
\]

50 很少：一个点就代表面积 2，硬模式面积估计很粗。固定是指所有时间、粒子和候选参数重复使用同一批坐标，而不是每次重新抽。

## 14. PF_REPLICATES=1 或 3 是什么意思？举例

同一参数 \(\theta\) 下，粒子滤波因随机路径不同会给不同值。例如三次得到：

\[
\log\widehat L_1=-101,\quad
\log\widehat L_2=-95,\quad
\log\widehat L_3=-104.
\]

若 PF_REPLICATES=1，只用某一次，如 -101。  
若为 3，当前代码计算：

\[
\overline\ell
=(-101-95-104)/3=-100,
\]

优化目标是 \(100\)（因为取负号最小化）。

重复能降低随机波动，但运行时间约乘 3。

重要：当前代码平均的是 log likelihood，即几何平均意义；不等于先平均 \(\widehat L_r\) 再取 log。详见问题 109。

## 15. PF_SEED 和 AREA_SEED 是什么意思？举例

随机数生成器本质上根据初始 seed 产生确定的伪随机序列。

- PF_SEED：控制隐藏激活、半径、消失事件、重采样位置等粒子滤波随机量；
- AREA_SEED：控制面积 Monte Carlo 点坐标。

例如：

    rng1 = np.random.default_rng(123)
    rng2 = np.random.default_rng(123)

二者生成的第一批数完全相同。把第二个 seed 改成 124，序列就不同。

PF_SEED 不控制合成数据模拟，因为模拟器另外传 seed=123。

## 16. 固定种子、同一积分点为什么能减少比较波动？

假设比较参数 A 和 B 的真实对数似然差只有 1。

若各自使用独立积分点：

\[
\widehat\ell_A=-100+\varepsilon_A,\qquad
\widehat\ell_B=-99+\varepsilon_B.
\]

若噪声分别是 \(+3,-2\)，观察差会被扭成 \(-4\)，错误地认为 A 更好。

若使用相同积分点，很多误差共同出现：

\[
\widehat\ell_A=-100+\varepsilon,\qquad
\widehat\ell_B=-99+\varepsilon,
\]

相减后共同误差抵消，仍差 1。这称为**公共随机数**或 common random numbers。

但不是任何情形都保证改善；关键是让两次输出误差正相关。固定 seed 也可能使目标成为某一固定随机样本下的近似，而非完全消除偏差，所以最后仍要换 seed 验证。

## 17. 平滑覆盖概率是什么意思？

硬覆盖函数是：

\[
I(d\le r)=
\begin{cases}
1,&d\le r,\\
0,&d>r.
\end{cases}
\]

soft 覆盖分数是：

\[
p_{\mathrm{cover}}
=\operatorname{sigmoid}\left(\frac{r-d}{\sigma}\right).
\]

- 圆内很深：接近 1；
- 边界 \(d=r\)：等于 0.5；
- 圆外很远：接近 0。

代码称它 probability，是把连续分数解释成“近似覆盖概率”；但它不是由原始随机圆盘机制严格推导出来的真实条件概率，而是一种人为平滑。

## 18. LIKELIHOOD_MODE="soft" 是什么意思？

该字符串决定面积和事件强度走哪个分支：

- mode=="exact"：用布尔数组，点只有在内/外两种状态；
- mode=="soft"：用 \(p_a(1-p_p)\) 作为连续激活未保护分数。

soft 下事件强度：

\[
\lambda_d p_a(x)[1-p_p(x)]
\]

可以取 0 与 \(\lambda_d\) 之间的任意值。这样距离边界略远的粒子不会立即得到零似然。

## 19. SOFT_SIGMA=0.10 和 MIN_EVENT_INTENSITY=1e-12

### SOFT_SIGMA

控制 sigmoid 从 0 过渡到 1 的空间宽度：

\[
\operatorname{sigmoid}((r-d)/\sigma).
\]

若 \(r-d=0.1\)：

- \(\sigma=0.1\)：sigmoid(1)\(\approx0.731\)；
- \(\sigma=0.01\)：sigmoid(10)\(\approx0.99995\)。

sigma 越小，边界越陡，更像硬指示。

### MIN_EVENT_INTENSITY

math.log(0) 无定义，会报错；数学扩展值是 \(-\infty\)。代码把事件强度限制为至少：

\[
\varepsilon=10^{-12}.
\]

于是：

\[
\log\varepsilon\approx-27.63.
\]

不匹配粒子受到巨大惩罚但不完全归零。

## 20. 为什么 soft 模式改变了模型？举例

原始模型断言：

> 圆外死亡强度严格为 0，圆内为 \(\lambda_d\)。

soft 模型断言：

> 圆外附近仍有正死亡强度，边界处约为一半。

例如半径 1，距离 1.02，sigma=0.1：

- 原模型：强度 0；
- soft：\(p_a\approx\operatorname{sigmoid}(-0.2)=0.450\)，若无保护，强度约 \(0.45\lambda_d\)。

所以 soft 不只是用更稳定的方式计算同一个数，而是对数据分布作了近似。减小 sigma 可逼近硬模型，但有限粒子下会加剧权重退化。

## 21. OPT_MAXITER、OPT_POPSIZE、POLISH_WITH_LBFGSB

- OPT_MAXITER=2：差分进化最多更新种群 2 代。2 代非常少，通常只能检查流程。
- OPT_POPSIZE=3：种群大小乘子。若有 \(d=2\) 个自由参数，SciPy 名义种群约为 \(3\times2=6\) 个候选。
- POLISH_WITH_LBFGSB=False：差分进化完成后，不启动自定义的 L-BFGS-B 局部精修。

大致函数评估上界（无固定维度、无 polish）与：

\[
(\text{maxiter}+1)\times\text{popsize}\times d
\]

同阶。这里约 \(3\times3\times2=18\) 次；每次又要运行 PF，所以即使设置小也可能慢。

正式配置要增加代数和种群，但先做 PF 噪声诊断，否则优化得更久可能只是更认真地拟合 Monte Carlo 噪声。

## 22. PF 噪声诊断和似然剖面开关

- RUN_PF_NOISE_DIAGNOSTIC=False：当前不执行重复 PF 诊断；
- PF_NOISE_REPEATS=3：若打开，固定参数重复 3 次，用不同 seed 看 loglik 波动；
- RUN_LIKELIHOOD_PROFILE=False：当前不扫描单个参数；
- PROFILE_GRID_SIZE=15：若打开，在 lambda_a_c 的范围选择 15 个值逐一计算似然。

例：真参数处三次 loglik 为 -100、-115、-94，标准差很大，说明当前 N 太小，优化结果不能稳定解释。

一维似然剖面会输出类似：

| lambda_a_c | loglik |
| ---: | ---: |
| 0.01 | -120 |
| 0.05 | -98 |
| 0.10 | -103 |

从而看峰值、平坦度和边界问题。

## 23. “Fixed T-zone definition, copied from the uploaded simulator”

翻译：

> 固定 T 形区域的定义，从上传的模拟器中复制而来。

它只是注释，不执行。下面的 x1、x2、y1、y2 把 \(10\times10\) 窗口分成三等份，用中间竖条与左横臂组成固定 T-zone。“fixed”表示该区域不随时间或粒子变化。

## 24. 固定时间窗注释的翻译和解释

翻译：

> 对似然推断推荐的模拟模式：固定时间观察窗比恰好在第 60 次死亡时停止更清晰。如果运行太慢，就设置 USE_FIXED_TIME_WINDOW=False。

固定时间设计预先规定观察 \([0,T]\)，数据包含：

- 窗口内所有事件；
- 最后事件到 T 的无事件信息。

若在第 60 次死亡停止，终点 \(T_{60}\) 本身是随机变量，并由事件过程决定。此时必须明确是在使用第 60 个事件到达时间的联合密度，还是条件于死亡数/停止时间。把随机终点直接当预先固定 T 容易混淆抽样机制。

注释最后一句有现实权衡：固定时间内死亡数可能很多，PF 更慢；按目标死亡数停止便于 tiny test。

## 25. hard indicator 和 smooth approximation

- **hard indicator**：硬指示函数，只有 0 或 1，在边界跳跃；
- **smooth approximation**：平滑近似，用连续可微或近似连续函数替代跳跃。

硬函数：

\[
\mathbf1\{r-d\ge0\}.
\]

平滑函数：

\[
\sigma_{\rm logit}((r-d)/\sigma).
\]

二者在离边界很远时近似一致，主要差别在边界附近。

## 26. “A smaller SOFT_SIGMA is closer ... but can be noisier”

翻译：

> 更小的 SOFT_SIGMA 会使近似更接近精确硬模型，但可能带来更大的噪声。

原因：sigma 小时，从近 1 到近 0 的过渡很陡。粒子路径或参数稍变一点，死亡点的覆盖分数就可能从 0.9 掉到 0.01，使权重和似然剧烈变化。有限粒子对这种尖锐观测更难覆盖，因此：

- 模型近似误差下降；
- Monte Carlo 方差、权重坍塌风险和优化粗糙度上升。

## 27. maxiter 和 popsize 翻译及含义

- maxiter：maximum iterations，最大迭代代数；
- popsize：population-size multiplier，种群规模乘子。

差分进化中的“一代”是让种群内候选依次尝试变异和替换，不等于一次 objective 调用。自由维数为 d 时，种群大约有 popsize×d 个成员，因此 maxiter 和 popsize 都会显著增加 PF 调用次数。

## 28. Diagnostics 注释翻译和解释

翻译：

> 诊断项。它们需要额外运行时间，但对调试推断非常有用。

“诊断”不是估计模型的主步骤，而是检查：

- 粒子似然是否随 seed 波动太大；
- 参数方向上是否存在清楚峰值；
- 死亡是否在 T-zone 富集；
- 真值与估计值差异是否只是 Monte Carlo 噪声。

它们慢，是因为每个诊断可能额外调用许多次完整 PF。

## 29. dataclass(frozen=True)“模拟不可修改对象”是什么意思？

ModelParams 使用：

    @dataclass(frozen=True)

创建后不能普通赋值：

    p.lambda_d = 2.0

会抛 FrozenInstanceError。需要：

    p2 = replace(p, lambda_d=2.0)

得到新对象，p 保持不变。

说“模拟”不可变，是因为 Python 对象内部并非数学意义绝对不可变；若字段本身含可变列表，列表内容仍可能变化。不过 ModelParams 字段全是 float，所以实践中可视为不可变。这样可防止优化时意外修改基准参数。

## 30. ParticleState 类逐行解释

    class ParticleState:

定义一种自定义数据类型，表示一个粒子的当前隐藏状态。

    # Each list contains tuples (x,y,r)

注释：两个列表的每个元素都是三元组 \((x,y,r)\)。

    active: List[Tuple[float, float, float]]

active 是列表；每个元素为三个浮点数，分别是激活圆盘圆心 x、圆心 y、半径 r。

    erk: List[Tuple[float, float, float]]

erk 结构相同，保存当前仍存在的 ERK 保护圆盘。

类型标注不会自动验证所有内容。真正创建时：

    ParticleState(active=[], erk=[])

后续 append 添加圆盘，pop 删除过期圆盘。

## 31. all 是什么？

Python 内置 all(iterable) 检查所有元素是否都为真：

    all([True, True, True])   # True
    all([True, False, True])  # False

代码：

    all(np.isfinite(vals))

要求八个参数全部有限。

    all(v > 0 for v in vals)

生成每个参数是否大于 0 的布尔值，并要求全部为 True。

空序列的 all([]) 按逻辑约定返回 True，但这里 vals 固定有八个元素。

## 32. np.isfinite 是什么？

逐元素判断数值是否为有限实数：

- 1.2、0、-5：True；
- np.inf、-np.inf、np.nan：False。

    np.isfinite([1.0, np.inf, np.nan])

得到：

    [True, False, False]

在 valid_params 中防止 NaN 或无穷参数进入模拟和优化。

## 33. 参数边界与 log-space 注释翻译和解释

翻译：

> 原始正参数的边界。优化器在对数空间工作。

原参数必须正，例如：

\[
0.02\le\lambda_{a,T}\le2.
\]

令 \(u=\log\lambda_{a,T}\)，则优化边界变为：

\[
\log0.02\le u\le\log2.
\]

优化完成后用 \(\lambda=e^u\) 返回原尺度。好处：

- 任意有限 u 指数化后自动为正；
- 跨数量级的参数更容易搜索；
- 乘法相对变化在 log 空间变成加法。

## 34. Dict[str, Tuple[float, float]] 是什么？

这是类型标注：

- Dict[K,V]：键类型 K、值类型 V 的字典；
- str：键是字符串；
- Tuple[float,float]：值是两个浮点数组成的元组。

所以 PARAM_BOUNDS 形如：

    {
        "lambda_d": (0.05, 5.0),
        "beta_a_R": (0.2, 8.0)
    }

字符串是参数名，二元组是下界和上界。

## 35. 三个 log 参数函数逐行解释

### unpack_log_params

    def unpack_log_params(log_vec, base, keys) -> ModelParams:

输入优化器的对数向量、完整基准参数和待替换字段名，返回完整 ModelParams。

    p = base

先让 p 指向基准对象。因为 ModelParams frozen，后面 replace 不会修改 base。

    for key, log_value in zip(keys, log_vec):

zip 配对。例如：

    keys = ["lambda_a_T", "lambda_a_c"]
    log_vec = [-0.693, -2.996]

依次得到 ("lambda_a_T",-0.693)、("lambda_a_c",-2.996)。

    p = replace(p, **{key: float(np.exp(log_value))})

步骤：

1. np.exp 把 log 参数还原为正数；
2. float 转 Python 浮点；
3. {key:value} 动态创建字段字典；
4. ** 拆成关键字参数；
5. replace 创建只替换该字段的新对象。

例如 key="lambda_a_T" 时等价于：

    p = replace(p, lambda_a_T=0.5)

    return p

返回完整参数对象。

### pack_log_params

    def pack_log_params(p, keys) -> np.ndarray:

把原参数对象转换为优化向量。

    getattr(p, key)

按字符串读取属性；key="lambda_d" 等价于 p.lambda_d。

    math.log(...)

取自然对数。

    [ ... for key in keys ]

对每个待估参数执行，形成列表。

    np.array(..., dtype=float)

转为浮点 NumPy 数组。

### log_bounds

    PARAM_BOUNDS[k][0]

读取参数 k 的下界；[1] 是上界。

    math.log(...)

把上下界取自然对数。

    return [(...) for k in keys]

为每个待估参数返回一个 log 边界二元组列表。

## 36. Sequence 是什么？

typing.Sequence[T] 表示“可按顺序访问的一串 T 元素”，通常支持 len 和索引。list、tuple、字符串等都属于序列概念。

使用 Sequence[float] 比 List[float] 更宽松：调用者可以传列表、元组或兼容序列，而函数只承诺读取，不要求 append。

它是类型提示，不会自动把输入转换为序列。

## 37. np.clip 是什么？

把数值限制在给定区间：

    np.clip([-100, -2, 3, 90], -50, 50)

结果：

    [-50, -2, 3, 50]

小于下界的变成下界，大于上界的变成上界。

代码把 sigmoid 输入限制到 [-50,50]，防止计算 exp(很大的正数) 溢出。

## 38. sigmoid 是什么？

sigmoid 或 logistic 函数：

\[
\sigma(z)=\frac1{1+e^{-z}}.
\]

性质：

- 输出始终在 (0,1)；
- \(\sigma(0)=0.5\)；
- z 很大时接近 1；
- z 很小时接近 0；
- 连续、平滑。

本代码用它把“到圆边界的带符号距离”变成软覆盖分数。

## 39. _sigmoid_clipped 逐行解释

    def _sigmoid_clipped(z: np.ndarray | float) -> np.ndarray | float:

z 可以是 NumPy 数组或单个 float；返回类型对应数组或 float。函数名前下划线表示内部辅助函数的命名惯例。

    np.clip(z, -50.0, 50.0)

先截断极端值。

    -np.clip(...)

取负数。

    np.exp(...)

逐元素计算指数。

    1.0 / (1.0 + ...)

得到 sigmoid。

例：z=[-2,0,2]，结果约 [0.119,0.5,0.881]。

## 40. np.ndarray 是什么？

ndarray 是 NumPy 的 N-dimensional array，即 N 维同质数组类型。

例如：

    a = np.array([[1.,2.],[3.,4.]])

- a 是 ndarray；
- a.shape 是 (2,2)；
- a.dtype 通常为 float64；
- a[:,0] 取第一列。

与 Python list 相比，ndarray 支持向量化运算：

    a ** 2

会逐元素平方，不需要手写循环。类型标注 np.ndarray 只说明预期输入是数组，没有指定精确形状。

# 第二部分：空间平滑、积分和隐藏传播（41–80）

## 41. 积分点数是什么意思？

要计算空间积分：

\[
\int_W f(x)\,dx
\]

代码不在连续空间每一点计算，而选 \(M\) 个代表点 \(U_1,\ldots,U_M\)：

\[
\int_W f(x)\,dx
\approx |W|\frac1M\sum_{m=1}^M f(U_m).
\]

M 就是积分点数 AREA_MC_POINTS。M=50 表示用 50 个样本代表面积 100 的整个窗口；M 越大一般越精确但越慢。

## 42. soft union 文档字符串翻译与原理

翻译：

> 对“点是否位于圆盘并集内”的指示函数作平滑近似。对一个圆盘，使用 sigmoid((半径−距离)/sigma)。对圆盘并集，使用所有圆盘中最大的边界分数。

对圆盘 j 定义：

\[
s_j(x)=r_j-\|x-c_j\|.
\]

- \(s_j>0\)：点在圆内；
- \(s_j=0\)：在边界；
- \(s_j<0\)：在圆外。

并集只要求至少一个圆覆盖，所以取：

\[
s(x)=\max_j s_j(x),
\qquad
p(x)=\operatorname{sigmoid}(s(x)/\sigma).
\]

这相当于找到“最能覆盖该点”的圆盘，再把它的边界距离平滑化。

## 43. np.full 是什么？

创建指定形状、全部填同一个值的数组：

    np.full(4, -1e9, dtype=float)

结果：

    [-1.e9, -1.e9, -1.e9, -1.e9]

代码用极小初值，随后用 np.maximum 逐圆盘更新最佳分数。它相当于“目前还没有任何圆盘候选”。

## 44. soft_union_probability_points 每一行

    def soft_union_probability_points(

定义同时处理多个空间点的函数。

    points: np.ndarray

形状预期为 \((M,2)\)，每行一个 \((x,y)\)。

    discs: Sequence[Tuple[float,float,float]]

圆盘序列，每个为 \((c_x,c_y,r)\)。

    sigma: float

平滑宽度。

    ) -> np.ndarray:

返回长度 M 的覆盖分数数组。

文档字符串见问题 42。

    n = points.shape[0]

读取点的行数 M。

    if len(discs) == 0:
        return np.zeros(n, dtype=float)

没有任何圆盘时，所有点覆盖分数为 0。

    scores = np.full(n, -1e9, dtype=float)

为每个点建立“当前最佳边界分数”，初始极小。

    px = points[:, 0]
    py = points[:, 1]

取所有点的 x 列和 y 列，长度都为 M。

    for cx, cy, r in discs:

逐圆盘解包圆心和半径。

    dist = np.sqrt((px-cx)**2 + (py-cy)**2)

一次向量化计算 M 个点到当前圆心的欧氏距离。

    scores = np.maximum(scores, r-dist)

逐元素取旧最佳值与当前圆盘 \(r-d\) 的较大者。循环结束后：

\[
\text{scores}_m=\max_j(r_j-d_{mj}).
\]

    return _sigmoid_clipped(scores / sigma)

除以平滑宽度后做 sigmoid，返回 M 个软覆盖分数。

## 45. soft_union_probability_one 每一行

此函数只处理一个点，数学与问题 44 相同。

    x: float, y: float

单个点坐标。

    discs

所有圆盘。

    sigma

平滑宽度。

    if len(discs) == 0:
        return 0.0

无圆盘，不覆盖。

    best = -1e9

初始化最佳边界分数。

    for cx, cy, r in discs:

逐个圆盘。

    dist = math.sqrt((x-cx)**2 + (y-cy)**2)

算单点欧氏距离。

    best = max(best, r-dist)

保留最大的 \(r-d\)。

    return float(_sigmoid_clipped(best / sigma))

变成软覆盖值，并强制转换为普通 Python float。

points 版本用于同时评估大量面积点；one 版本用于某一个观测死亡位置。

## 46. area_points 是预先均匀抽取的 M 个空间点，什么意思？

例如窗口 \(W=[0,10]^2\)，代码独立抽：

\[
X_m\sim U(0,10),\qquad Y_m\sim U(0,10),
\]

组成 \(U_m=(X_m,Y_m)\)。这些点不是死亡，也不是粒子中心，只是用于数值积分的“探针”。

“预先”表示在优化开始前生成一次；之后反复用相同坐标检测每个粒子的 active/ERK 覆盖。

## 47. 原始字符串前缀 r 和反斜杠是什么意思？

普通 Python 字符串中反斜杠启动转义：

    "\n"

表示换行，不是两个普通字符。

原始字符串：

    r"\n"

通常保留反斜杠和 n 本身。

代码：

    r"""Approximate |A(Va) \ A(Vp)| ..."""

使用 r，避免集合差符号中的反斜杠被当成转义开头。三引号允许多行文档字符串。

## 48. 按位或 |= 累积是什么意思？

active 是布尔数组。表达式：

    active |= condition

等价于：

    active = active | condition

逐元素逻辑“或”。

例：

    active    = [False, True, False]
    condition = [True,  False, False]

更新后：

    [True, True, False]

遍历每个圆盘时，只要某点被任意一个圆盘覆盖，它的位置就永久变 True，从而得到圆盘并集。

## 49. np.random.default_rng(seed) 是什么？

创建 NumPy 推荐的新式随机数生成器 Generator。

    rng = np.random.default_rng(123)

之后可调用：

- rng.uniform：均匀分布；
- rng.exponential：指数分布；
- rng.integers：随机整数。

相同 seed 和相同调用顺序产生相同伪随机结果。Generator 把随机状态封装在 rng 中，避免依赖全局 np.random 状态。

## 50. 模拟器文档字符串翻译

原文：

> Simulate the original model and return death events plus hidden histories.

翻译：

> 模拟原始模型，并返回死亡事件以及隐藏过程的历史记录。

死亡事件 death_events 是观测数据；cas_events 是隐藏激活事件历史。当前返回的“hidden histories”并不包括每个时刻完整圆盘快照，只包括被接受的 caspase 激活事件表；ERK 事件可由死亡与随机半径生成过程理解。

## 51. return 字典逐行解释

    return {

返回一个字典。

    "death_events": np.array(death_events, dtype=float)

把死亡列表转成浮点数组；通常每行 \((x,y,t)\)。

    "cas_events": np.array(cas_events, dtype=float)

把隐藏激活事件列表转成浮点数组。

    "final_time": np.array([t], dtype=float)

把最终时间 t 包成长度 1 的浮点数组。这里完全可以直接返回 float(t)，当前写法只是统一用数组。

调用者通过字符串键读取：

    sim["death_events"]
    sim["final_time"][0]

## 52. mode、sigma：硬/软似然及平滑宽度

- mode 是字符串，决定用 exact 还是 soft；
- sigma 只在 soft 模式参与公式，控制边界过渡宽度。

“硬/软似然”更准确说是“似然计算中采用硬或软的几何覆盖函数”。整个似然还包含无事件积分和事件强度。

## 53. 无死亡区间的 log survival factor 是什么？推导

给定某条粒子隐藏路径，在时刻 s 的空间总死亡 hazard 为：

\[
h_s
=\int_W\lambda^d(x,s)\,dx
=\lambda_d|A(V_s^a)\setminus A(V_s^p)|.
\]

设从 \(t_0\) 到 t 没有死亡的条件概率为：

\[
S(t)=P(N(t_0,t]=0\mid Z).
\]

在小区间 \([t,t+dt]\)：

\[
P(\text{无死亡}\mid\text{此前无死亡})
=1-h_tdt+o(dt).
\]

所以：

\[
S(t+dt)=S(t)[1-h_tdt+o(dt)].
\]

移项除以 dt 并取极限：

\[
S'(t)=-h_tS(t),\qquad S(t_0)=1.
\]

解为：

\[
S(t_1)
=\exp\left(-\int_{t_0}^{t_1}h_sds\right).
\]

取对数：

\[
\log S(t_1)
=-\int_{t_0}^{t_1}
\lambda_d|A(V_s^a)\setminus A(V_s^p)|ds.
\]

这就是函数返回的 log_survival。它越负，表示该粒子认为本区间本应很容易死亡，却实际一个死亡都没观测到，因此该粒子越不可信。

## 54. 点过程似然为什么是指数积分乘事件强度乘积？

先看一次事件。下一事件在 s 前不发生的概率是：

\[
S(s)=\exp(-\int_{t_0}^{s}h_u du).
\]

在 s 附近发生事件的条件概率约为 \(h_sds\)，所以事件时间密度：

\[
f(s)=S(s)h_s.
\]

对多次事件 \(s_1<\cdots<s_n\)，逐区间使用条件概率：

\[
\prod_{k=1}^n
\left[
\exp\left(-\int_{s_{k-1}}^{s_k}h_u du\right)
h_{s_k}
\right]
\times
\exp\left(-\int_{s_n}^{T}h_u du\right).
\]

所有指数项合并：

\[
L
=\exp\left(-\int_0^T h_u du\right)
\prod_{k=1}^n h_{s_k}.
\]

时空点过程还要包括事件位置密度，因此每个事件贡献局部强度 \(\lambda(x_k,s_k)\)，而积分是：

\[
\int_0^T\int_W\lambda(x,s)\,dx\,ds.
\]

最终：

\[
L
=\exp\left(-\int_0^T\int_W\lambda(x,s)\,dx\,ds\right)
\prod_k\lambda(x_k,s_k).
\]

## 55. log_survival 是什么意思？

survival 在这里不是“细胞存活时间”的生物学总概率，而是**该观测区间没有出现死亡点事件的概率**。

log_survival 是它的自然对数：

\[
\log S=-\int h_sds\le0.
\]

用 log：

- 多个区间的概率乘法变加法；
- 避免极小概率下溢为 0；
- 方便与事件项 log(lambda) 相加。

## 56. 没有隐藏事件时为什么减 \(h_s(t_1-t)\)？

如果在剩余区间状态不变，那么 active/ERK 几何不变，总 hazard \(h_s=h\) 是常数：

\[
\int_t^{t_1}h_sds=h(t_1-t).
\]

所以：

\[
\log S\leftarrow\log S-h(t_1-t).
\]

例：h=2，剩余长度 0.5，则无死亡概率：

\[
e^{-2\times0.5}=e^{-1},
\]

其 log 为 -1，所以代码减 1。

## 57. 隐藏事件发生在区间内时的分段积分

若从当前 t 到下一个隐藏跳跃经历 \(\Delta t\)，在跳跃前状态不变，hazard 是当前常数 h：

\[
\int_t^{t+\Delta t}h_sds=h\Delta t.
\]

因此：

    log_survival -= death_hazard * dt
    t += dt

到达跳跃时刻后，active 或 ERK 列表改变，重新计算新 hazard，再积分下一段。这对给定模拟路径的时间积分是精确的分段常数积分；但每段的空间面积 death_area 仍是 Monte Carlo 近似。

## 58. death hazard 翻译和解释

hazard 可译为**风险率、危险率、瞬时发生率**。death hazard 是在给定当前历史和隐藏状态下，“下一瞬间全空间发生死亡事件的瞬时总率”。

若 \(h_t=3/\text{小时}\)，小时间 \(dt=0.01\) 小时内发生一个死亡的概率近似 \(3\times0.01=0.03\)。

它不是普通概率，单位是每时间；可以大于 1。

## 59. 为什么 \(h_s=\lambda_d\times death\_area\)？

局部时空强度在可死亡区域 \(D_s\) 上恒为 \(\lambda_d\)，其他地方为 0：

\[
\lambda(x,s)=\lambda_d\mathbf1\{x\in D_s\}.
\]

全空间总率：

\[
h_s=\int_W\lambda(x,s)dx
=\lambda_d\int_W\mathbf1\{x\in D_s\}dx
=\lambda_d|D_s|.
\]

下一次隐藏跳跃前，圆盘集合不变，因此 \(D_s\) 和 \(h_s\) 不变。

## 60. Returns log survival factor 那句话

翻译：

> 返回对数生存因子：从 \(t_0\) 到 \(t_1\)，\(-\lambda_d\) 乘以激活但未保护区域面积的时间积分。

严格公式：

\[
-\int_{t_0}^{t_1}
\lambda_d
|A(V_t^a)\setminus A(V_t^p)|\,dt.
\]

双反斜杠 \\ 只是 Python 文档字符串中显示集合差反斜杠所需的写法。

## 61. death_area 与 death_hazard 两行

    death_area = active_unprotected_area(...)

根据当前粒子 st 的 active、ERK 圆盘，利用 area_points 估计：

\[
|A(V^a)\setminus A(V^p)|.
\]

mode 和 sigma 决定硬/软方法。

    death_hazard = p.lambda_d * death_area

单位面积死亡率乘可死亡面积，得到全空间单位时间死亡总率。

## 62. 隐藏传播代码逐行

    if a0_hidden <= 0.0:

若激活候选、active 消失、ERK 消失的总隐藏率不正，未来没有隐藏跳跃。

    log_survival -= death_hazard * (t1-t)

当前 hazard 保持到终点，积完整剩余时间。

    break

退出 while。

    dt = rng.exponential(1.0/a0_hidden)

抽下一隐藏事件等待时间。NumPy exponential 的参数是均值 scale，所以传总率的倒数。

    if t+dt >= t1:

若下一隐藏事件晚于区间终点，则观察区间内没有该跳跃。

    log_survival -= death_hazard * (t1-t)
    t = t1
    break

只积到 t1，标记到达终点并退出。

若 t+dt<t1：

    log_survival -= death_hazard * dt
    t += dt

积到实际隐藏跳跃时刻，并推进时间；后面选择隐藏事件类别并更新状态。

## 63. return log_survival 到底算什么？

它返回当前粒子在 \([t_0,t_1]\) **一个死亡都没出现**的条件概率的对数：

\[
\log P(N(t_0,t_1]=0\mid Z^{(i)},\theta).
\]

随后 particle_loglikelihood 再加终点死亡的 log 强度，形成完整区间增量 logG。

## 64. “数值稳定求和与系统重采样”是什么意思？

包含两个独立工具：

1. **数值稳定求和**：在 log 域计算许多极小权重的总和，避免浮点上/下溢；
2. **系统重采样**：按粒子权重复制高权重粒子、淘汰低权重粒子，只随机一个起点，位置等间隔。

## 65. 为什么需要计算 \(\log\sum_i e^{a_i}\)？

在代码中：

\[
a_i=\log w_{k-1}^{(i)}+\log G_k^{(i)}
=\log\widetilde w_k^{(i)}.
\]

当前观测的增量似然是未归一化权重和：

\[
\widehat c_k=\sum_i\widetilde w_k^{(i)}
=\sum_i e^{a_i}.
\]

累计的是对数似然，所以需要：

\[
\log\widehat c_k
=\log\sum_i e^{a_i}.
\]

## 66. exp 为什么会上溢或下溢？

计算机浮点范围有限。float64 大致：

- exp(1000) 太大，变成 inf，叫上溢；
- exp(-1000) 太小，舍入为 0，叫下溢。

若 log 权重是 [-1000,-1001]，直接指数化都可能接近 0，求和后 log(0) 错误；但真实 logsumexp 约 -999.687。

减去最大值 m 后指数输入变成 [0,-1]，安全计算：

\[
m+\log(e^0+e^{-1}).
\]

## 67. np.isfinite 再解释

它判断输入是否不是 NaN、正无穷或负无穷。用于：

- 参数合法性；
- 增量似然是否数值崩溃；
- PF 是否返回有效值。

标量输入返回 bool，数组输入返回布尔数组。

## 68. np.inf 是什么？

NumPy 的浮点正无穷：

    np.inf

负无穷：

    -np.inf

优化中：

- 无效 loglik 返回 -inf，表示不可能/极差；
- 最佳 loglik 初始设 -inf，任何有限值都比它大；
- 最小目标 best 初始设 +inf，任何有限目标都比它小。

它们是 IEEE 浮点特殊值，不是一个非常大的普通有限数。

## 69. logsumexp 中最大值非有限为什么返回 -inf？

代码：

    m = float(np.max(a))
    if not np.isfinite(m):
        return -np.inf

常见合理情形是所有 \(a_i=-\infty\)，说明所有粒子权重为 0；总和为 0：

\[
\log0=-\infty.
\]

所以返回 -inf。

但这个自写函数并非一般情况下完全严谨：

- 若某个 a_i=+inf，数学 logsumexp 应为 +inf，代码却返回 -inf；
- 若含 NaN，也返回 -inf，掩盖了 NaN 原因。

在本应用中 a_i 正常应不大于有限范围，+inf 表示严重数值失败；作者统一把任何非有限情况当作候选失败。正式代码可直接使用 scipy.special.logsumexp 并单独检查 NaN。

## 70. np.cumsum 是什么？

累计和：

    np.cumsum([0.1, 0.6, 0.3])

得到：

    [0.1, 0.7, 1.0]

第 j 项等于前 j 项权重之和。重采样时它把 [0,1] 划分成长度分别为各权重的区间。

## 71. systematic_resample 原理和代码

设权重 \(w=(0.1,0.6,0.3)\)，N=3。

    n = len(weights)

n=3。

    positions = (rng.uniform() + np.arange(n))/n

抽一个 \(U\sim U(0,1)\)，构造：

\[
\frac U3,\frac{U+1}3,\frac{U+2}3.
\]

三个位置相隔 \(1/3\)，都落在 [0,1)。

    cumsum = np.cumsum(weights)

得到 [0.1,0.7,1.0]。

    cumsum[-1] = 1.0

纠正浮点累加误差，保证最后覆盖到 1。

    np.searchsorted(cumsum, positions, side="right")

看每个位置落在哪个累计区间：

- [0,0.1)：祖先 0；
- [0.1,0.7)：祖先 1；
- [0.7,1]：祖先 2。

高权重区间更长，会接到更多等距位置，因此产生更多后代。

## 72. np.searchsorted 和 np.cumsum

np.cumsum：构造累计权重边界。  
np.searchsorted(sorted_array, values)：对每个 value 找到插入有序数组的位置，使顺序不被破坏。

例如：

    np.searchsorted([0.1,0.7,1.0], [0.05,0.4,0.9], side="right")

得到 [0,1,2]，正好是祖先索引。

side="right" 规定恰好等于边界时放右侧；连续均匀随机数正好命中边界的理论概率为 0。

## 73. 重采样阈值和 soft/exact 配置是什么意思？

函数参数：

- resample_threshold=0.5：若 ESS < 0.5N 就重采样；
- mode：选择 hard/exact 或 soft；
- sigma：soft 的平滑宽度。

阈值过高会频繁重采样、损失路径多样性；过低会让少数巨大权重长期支配。0.5N 是常用起点，不是普适最优值。

## 74. \(\log\widehat p_\theta(Y_{0:T}^d)\) 是随机 Monte Carlo 近似，什么意思？

真正似然要对所有可能隐藏路径积分：

\[
p_\theta(Y)
=\int p_\theta(Y,Z)\,dZ.
\]

隐藏路径空间极大，无法解析积分。粒子滤波用 N 条随机路径近似：

\[
\widehat p_\theta(Y).
\]

帽子表示估计。换 PF seed 会换粒子路径，所以同一 \(\theta,Y\) 的估计值会变化。取自然对数得到函数输出。

## 75. 粒子滤波近似对数似然是什么？

粒子滤波按死亡时间顺序构造每一段预测似然：

\[
\widehat c_k
\approx p_\theta(Y_k\mid Y_{1:k-1}),
\]

再累加：

\[
\log\widehat L
=\sum_k\log\widehat c_k.
\]

因此它既进行隐藏状态过滤，也顺便提供观测数据似然估计，供外层优化参数。

## 76. Bootstrap particle estimate of log p... 翻译

翻译：

> 使用 bootstrap 粒子滤波，对死亡观测 \(Y_{0:T}^d\) 在参数 \(\theta\) 下的对数概率（对数似然）进行估计。

bootstrap 表示提议分布直接采用状态转移，不用当前观测构造更聪明的 proposal；不是这里的经典数据重抽样 bootstrap 置信区间。

## 77. particle_loglikelihood 参数逐行

- death_events: np.ndarray：死亡数组，每行 x、y、t；
- p: ModelParams：当前被评价的完整参数；
- T_end: float：观察终点；
- n_particles=N_PARTICLES：粒子数，未传时取全局 20；
- area_points: np.ndarray | None=None：可提供固定积分点；None 时内部生成；
- seed=PF_SEED：本次 PF 随机种子；
- resample_threshold=RESAMPLE_THRESHOLD：ESS 重采样比例阈值；
- mode=LIKELIHOOD_MODE：exact/soft；
- sigma=SOFT_SIGMA：平滑宽度；
- verbose=False：是否打印额外错误信息；
- -> float：返回一个普通浮点对数似然。

等号右边是默认值，冒号右边是类型提示。

## 78. 生成面积积分点是什么意思？

若 area_points=None，函数自行抽 M 个均匀坐标，形成 \((M,2)\) 数组，用于每次 active_unprotected_area。它不是时间积分点；时间积分由隐藏跳跃区间分段完成。

## 79. np.column_stack 是什么？

把一维数组按列拼接：

    x = [1,2,3]
    y = [4,5,6]
    np.column_stack([x,y])

得到：

    [[1,4],
     [2,5],
     [3,6]]

代码把 M 个 x 坐标和 M 个 y 坐标组成 M 个空间点。

## 80. common random numbers 翻译和解释

翻译：**公共随机数法、共同随机数法**。

它是比较随机系统时的方差缩减技术：让候选 A 和 B 使用相同随机输入，使共同噪声在差值中抵消。代码最明确地对 area_points 使用此思想。

固定 PF seed 也试图产生类似效果，但参数改变会改变接受/拒绝次数和随机数消费顺序，之后的随机流可能错位，所以 PF 路径层面的“共同随机数”耦合并不总是强。

# 第三部分：粒子权重、似然与完整主循环（81–120）

## 81. argsort 是什么意思？

np.argsort(a) 不直接返回排好序的值，而返回“按什么索引顺序取就能排序”。

例如：

    a = [30,10,20]
    np.argsort(a)

得到 [1,2,0]，因为 a[1]=10、a[2]=20、a[0]=30。

代码对死亡时间列 death_events[:,2] 做 argsort，再用 death_events[order] 重排行，确保时间递增。

## 82. 防御性检查是什么意思？

即使前面已经排序，函数仍检查：

    if s_d < t_prev:
        raise ValueError(...)

这是为了防止未来代码被修改、数据含异常或函数被独立调用时悄悄产生错误。它不是模型公式的一部分，而是软件可靠性措施。

## 83. 事件强度项和 \(G_k^{(i)}\) 的原理

第 i 个粒子在区间 \((s_{k-1},s_k)\) 给出隐藏路径。观测内容是：

1. 区间内没有死亡；
2. 在 \(s_k\) 的位置 \((x_k,y_k)\) 出现死亡。

第 1 部分条件概率：

\[
\exp\left(-\int_{s_{k-1}}^{s_k}h_s^{(i)}ds\right).
\]

第 2 部分的时空事件密度：

\[
\lambda_i
=\lambda_\theta^d(x_k,y_k,s_k\mid Z_{s_k-}^{(i)}).
\]

两者相乘：

\[
G_k^{(i)}
=\exp\left(-\int h_s^{(i)}ds\right)\lambda_i.
\]

取 log：

\[
\log G_k^{(i)}
=-\int h_s^{(i)}ds+\log\lambda_i.
\]

propagate_hidden_until 先返回负积分 val；代码 val += log(lam_event) 正好得到 \(\log G_k^{(i)}\)。

必须用预跳 \(Z_{s_k-}\)，因为这次死亡触发的 ERK 是事件发生之后才加入，不能反过来保护并阻止它自己。

## 84. logG[i] 是什么？

logG 是长度 N 的数组。logG[i] 保存第 i 条隐藏路径对“当前一个观测区间”的对数支持度：

\[
\text{logG}[i]=\log G_k^{(i)}.
\]

它不是累计到最终时间的 loglik，也不是归一化权重。随后每个元素与旧 logw[i] 相加，形成当前未归一化后验对数权重。

## 85. 为什么 \(\widetilde w_k^{(i)}=w_{k-1}^{(i)}G_k^{(i)}\)？推导

在第 k 次观测前，预测隐藏分布近似为：

\[
p(dz_k\mid Y_{1:k-1})
\approx\sum_i w_{k-1}^{(i)}\delta_{z_k^{(i)}}(dz_k).
\]

Bayes 公式：

\[
p(dz_k\mid Y_{1:k})
\propto
p(Y_k\mid z_k,Y_{1:k-1})
p(dz_k\mid Y_{1:k-1}).
\]

记：

\[
G_k(z_k)=p(Y_k\mid z_k,Y_{1:k-1}).
\]

把粒子经验测度代入：

\[
p(dz_k\mid Y_{1:k})
\propto
\sum_i
w_{k-1}^{(i)}G_k(z_k^{(i)})
\delta_{z_k^{(i)}}(dz_k).
\]

所以第 i 个原子的新未归一化质量就是：

\[
\widetilde w_k^{(i)}
=w_{k-1}^{(i)}G_k^{(i)}.
\]

bootstrap proposal 等于状态转移，所以一般重要性权重中的“目标转移/proposal”比值抵消，只剩观测增量 \(G_k\)。

## 86. logsumexp 保证数值稳定是什么意思？

不改变数学值，而改写计算方式：

\[
\log\sum_i e^{a_i}
=m+\log\sum_i e^{a_i-m},
\quad m=\max_i a_i.
\]

最大的指数变成 \(e^0=1\)，其余不超过 1，避免上溢；也避免所有极小数先被舍入成 0。详见问题 65–69。

## 87. verbose=True 时打印死亡编号是什么意思？

verbose 是“详细输出”开关。

- False：坍塌时安静返回 -inf，避免优化时打印太多；
- True：打印例如 “All particles collapsed at observed death 5.”，帮助定位是第几个死亡导致失败。

它只影响输出，不改变计算。

## 88. 返回 \(-\infty\) 是什么意思？

对数似然：

\[
\log0=-\infty.
\]

返回 -inf 表示该候选参数下观测数据的粒子似然为 0，或计算已数值失败。外层 objective 检测非有限值并返回 1e90 巨大正目标，使最小化器拒绝该候选。

## 89. 为什么累计似然是乘积、log 是加法？

概率链式法则：

\[
p(Y_{1:k})
=p(Y_{1:k-1})
p(Y_k\mid Y_{1:k-1}).
\]

递推：

\[
p(Y_{1:n})
=\prod_{k=1}^n
p(Y_k\mid Y_{1:k-1}).
\]

粒子滤波用：

\[
\widehat c_k
=\sum_iw_{k-1}^{(i)}G_k^{(i)}
\]

近似第 k 个条件概率/密度。因此：

\[
\widehat L_k
=\widehat L_{k-1}\widehat c_k,
\quad
\widehat L_n=\prod_k\widehat c_k.
\]

取对数：

\[
\log\widehat L_k
=\log\widehat L_{k-1}+\log\widehat c_k.
\]

代码 loglik += inc 正是这一步。

## 90. 归一化对数权重为什么使普通权重和为 1？

定义：

\[
\widehat c_k=\sum_j\widetilde w_k^{(j)}.
\]

普通归一化：

\[
w_k^{(i)}
=\frac{\widetilde w_k^{(i)}}{\widehat c_k}.
\]

所以：

\[
\sum_iw_k^{(i)}
=\frac{\sum_i\widetilde w_k^{(i)}}{\widehat c_k}=1.
\]

取 log：

\[
\log w_k^{(i)}
=\log\widetilde w_k^{(i)}
-\log\widehat c_k.
\]

代码 inc=\(\log\widehat c_k\)，所以 logw = new_logw_unnorm - inc。

## 91. ESS 小于阈值后的步骤是什么意思？

假设 N=10，权重大约：

\[
(0.7,0.2,0.1,0,\ldots).
\]

虽然有 10 个数组元素，实际上信息主要来自 3 个粒子，ESS 很低。

系统重采样会大约：

- 复制第 1 粒子 7 次；
- 第 2 粒子 2 次；
- 第 3 粒子 1 次。

每个后代随后赋等权 0.1。旧权重的信息已经体现在复制次数里，不能再保留旧权重，否则重复计算。

clone_state 创建独立 active/erk 列表。否则 7 个后代可能引用同一个列表，对其中一个 append 会同时污染全部。

重采样解决权重退化，但会造成样本贫化：多个后代初始状态相同，只能靠后续随机传播重新分散。

## 92. t_prev 更新成 s_d 是什么意思？

当前循环已经处理：

\[
[t_{\mathrm{prev}},s_d]
\]

的无死亡积分和在 \(s_d\) 的死亡。下一次死亡应从当前死亡时刻继续：

    t_prev = float(s_d)

若死亡时间为 0.3、0.8、1.1，区间依次是 [0,0.3]、[0.3,0.8]、[0.8,1.1]，不会重复或漏掉时间。

## 93. area_points is None 代码

    if area_points is None:

调用者没提供积分点时才生成。

    rng_area = np.random.default_rng(AREA_SEED)

建立固定种子的面积随机生成器。

    rng_area.uniform(0.0,Lx,M)

生成 M 个 [0,Lx) 均匀 x 坐标。

    rng_area.uniform(0.0,Ly,M)

生成 M 个 y 坐标。

    np.column_stack([...])

拼成 M 行 2 列，每行 \((x_m,y_m)\)。

## 94. order = np.argsort(death_events[:,2])

- death_events[:,2]：取所有行第 3 列，即时间；
- np.argsort：返回时间从小到大的行索引；
- death_events[order]：按该索引重排整个事件表。

例：时间 [0.8,0.2,0.5]，order=[1,2,0]。

## 95. np.full 再解释

函数：

    np.full(shape, fill_value, dtype)

创建指定形状并填满同一值。

本代码两处典型用途：

    np.full(n, -1e9)

初始化 soft 几何最大分数；

    np.full(N, -math.log(N))

初始化所有粒子的相同 log 权重。

## 96. states 列表推导式

    states = [
        ParticleState(active=[], erk=[])
        for _ in range(n_particles)
    ]

循环 n_particles 次，每次创建新的 ParticleState。下划线 _ 表示循环编号不使用。

重要：每次都执行 active=[]，所以粒子拥有不同列表，不是共享一个列表对象。

## 97. enumerate 是什么？

enumerate 同时给“编号”和“元素”：

    for i, value in enumerate(["a","b"], start=1):

依次得到 (1,"a")、(2,"b")。

代码：

    for k, (x_d,y_d,s_d) in enumerate(death_events,start=1)

同时取得第几个死亡和该行三个值。

    for i, st in enumerate(states)

同时取得粒子索引 i 与状态 st，默认 i 从 0。

## 98. pre-jump 翻译和解释

pre-jump：**跳跃前、跃迁前**。

\[
Z_{s-}=\lim_{u\uparrow s}Z_u
\]

表示时刻 s 左极限，即事件发生前一瞬间状态。

死亡强度必须用 \(Z_{s-}\)；先判断死亡前是否 active 且未保护，死亡发生后才增加 ERK 圆盘。若用 \(Z_s\)，新 ERK 会错误地影响触发它自己的死亡。

## 99. 面积点和死亡数组预处理逐行

前半部分见问题 93。

    if death_events.size == 0:

NumPy size 是总元素数；0 表示没有死亡。

    death_events = np.empty((0,3), dtype=float)

构造 0 行 3 列空表。这样后面 death_events[:,2] 等二维操作结构一致。

    else:
        death_events = np.asarray(death_events,dtype=float)

把列表或数组统一转为浮点 ndarray；若本来就是合适数组，可能避免不必要复制。

    order = np.argsort(death_events[:,2])

按时间列得到排序索引。

    death_events = death_events[order]

重排整行。

## 100. 粒子滤波主循环逐行解释

    # Process observed deaths in chronological order.

注释：按时间顺序处理死亡。

    for k,(x_d,y_d,s_d) in enumerate(death_events,start=1):

逐死亡读取编号、位置和时刻。

    if s_d < t_prev:
        raise ValueError(...)

防止时间倒退。

    logG = np.empty(n_particles,dtype=float)

为当前死亡分配 N 个增量 log 似然槽位。empty 不初始化内容，但下面每个 i 都会写入。

    for i,st in enumerate(states):

逐粒子计算。

    val = propagate_hidden_until(...)

从上一死亡传播隐藏过程到当前死亡前，直接修改 st，并返回无死亡 log 生存项。

    lam_event = death_event_intensity(...)

用死亡前状态计算当前观测位置的局部死亡强度。

    val += math.log(lam_event)

加入事件强度对数，得到 \(\log G_k^{(i)}\)。

    rE = rng.exponential(1.0/p.beta_d_R)

为当前死亡在第 i 个粒子中抽隐藏 ERK 半径。

    st.erk.append((x_d,y_d,rE))

死亡之后把 ERK 保护圆盘加入状态。

    logG[i] = val

保存粒子 i 的增量。

    new_logw_unnorm = logw + logG

实现 \(\log\widetilde w=\log w+\log G\)。

    inc = logsumexp_np(new_logw_unnorm)

计算 \(\log\sum_i\widetilde w_i\)，即当前增量 loglik。

    if not np.isfinite(inc):

若坍塌或数值失败：

    if verbose: print(...)

可选打印编号。

    return -np.inf

终止当前候选参数评估。

    loglik += inc

累计观测似然。

    logw = new_logw_unnorm-inc

归一化 log 权重。

    weights = np.exp(logw)

回普通权重计算 ESS。

    neff = 1.0/np.sum(weights**2)

有效样本量。

    if neff < resample_threshold*n_particles:

低于阈值才重采样。

    ancestors = systematic_resample(weights,rng)

得到每个新粒子的祖先索引。

    states = [clone_state(states[int(j)]) for j in ancestors]

复制相应状态，并确保列表独立。

    logw.fill(-math.log(n_particles))

把 logw 每个元素重设为 \(\log(1/N)\)。

    t_prev = float(s_d)

准备下一时间区间。

最后无死亡区间：

    if T_end > t_prev:

终点晚于最后死亡才需传播。

    logG = np.empty(N)

为每个粒子的最终无事件因子分配空间。

    logG[i] = propagate_hidden_until(...)

这里只包含生存项，没有终点事件强度。

    new_logw_unnorm = logw+logG
    inc = logsumexp_np(...)

对隐藏路径取加权平均，得到最后无事件区间的边际概率。

    if not np.isfinite(inc): return -np.inf
    loglik += inc

检查并累计。

    return float(loglik)

返回完整观察窗的粒子 loglik。

## 101. 基准参数和待估参数名是什么？

- base_params：完整八参数对象，提供不估计参数的固定值，也提供待估参数被替换前的值；
- keys：字符串序列，说明优化器能改变哪些字段。

例如 keys=("lambda_a_T","lambda_a_c")，则 lambda_d、beta 等保持 base_params 的值。

## 102. 在对数参数空间最大化粒子似然是什么意思？

优化变量不是 \(\lambda\)，而是：

\[
u=\log\lambda.
\]

优化器寻找 u，使粒子似然最大；每次评价前用 \(\lambda=e^u\) 恢复。这样自然保证 \(\lambda>0\)。外部 SciPy 实际最小化负 loglik。

## 103. 固定 area_points 防止候选碰巧获得有利网格

若参数 A 的积分点恰好多落在 active 区，估计 death_area 偏大；参数 B 的点恰好少落，偏小。若每个候选重新抽网格，优化器可能把这种随机幸运当参数优势。

全部候选使用同一坐标后，空间积分误差更共同，参数差异更可比。这降低比较方差，但不消除 50 点本身的离散误差。

## 104. nonlocal 是什么？为什么字典不需要？

嵌套函数若给外层普通变量重新赋值：

    x = 0
    def f():
        x += 1

Python 会把 f 中的 x 当局部变量，读取前未赋值，报错。需写：

    nonlocal x

本代码：

    eval_counter = {"n":0}
    def objective(...):
        eval_counter["n"] += 1

没有给名字 eval_counter 重新绑定，只修改它指向的字典内容，因此不需要 nonlocal。

## 105. objective 为什么返回负平均对数似然？

差分进化调用形式是“最小化 objective”。但我们想：

\[
\max_\theta \ell(\theta).
\]

等价于：

\[
\min_\theta -\ell(\theta).
\]

优化器提出 log_vec；objective：

1. 转回完整参数；
2. 跑 R 次 PF；
3. 求平均 loglik；
4. 加负号返回。

obj 越小，loglik 越大。

## 106. pf_seed + 1009 * r 是什么？

r 是重复编号 0、1、2...。种子依次：

\[
\text{pf\_seed},\quad
\text{pf\_seed}+1009,\quad
\text{pf\_seed}+2018,\ldots
\]

1009 只是选的整数间隔，没有统计学神秘意义。目的仅是让各重复不使用完全相同的随机流，同时保持可复现。

## 107. 非有限似然为何给 1e90 惩罚？

若 ll=-inf 或 NaN，不能作为正常目标比较。最小化器喜欢小值，所以返回巨大正数：

\[
10^{90}
\]

告诉优化器“此候选极差，不要选”。

1e100 用于参数非法，1e90 用于 PF 失败；二者具体大小没有理论意义，只需远大于正常目标。过大值可能影响某些梯度算法，但差分进化主要比较大小。

## 108. obj 公式是什么意思？

\[
\text{obj}
=-\frac1R\sum_{r=1}^R\log\widehat L_r(\theta).
\]

- R：PF_REPLICATES；
- \(\widehat L_r\)：第 r 次随机 PF 似然估计；
- 先取各自 log；
- 求算术平均；
- 取负供最小化。

这等价于最小化负的 log 几何平均：

\[
\frac1R\sum_r\log\widehat L_r
=\log\left[
\left(\prod_r\widehat L_r\right)^{1/R}
\right].
\]

## 109. 平均 loglik 数学上合理吗？

需要区分“实用”与“严格目标”。

bootstrap PF 在标准条件下通常给似然 \(L\) 的无偏估计：

\[
E[\widehat L]=L.
\]

但 Jensen 不等式给出：

\[
E[\log\widehat L]\le\log E[\widehat L]=\log L.
\]

所以 log PF 估计一般向下偏。平均多个 log：

\[
\frac1R\sum_r\log\widehat L_r
\]

降低方差，但不会消除这种偏差；它优化的是几何平均的随机替代目标。

另一种写法是先平均似然再取 log：

\[
\log\left(\frac1R\sum_r\widehat L_r\right)
=\operatorname{logsumexp}(\ell_1,\ldots,\ell_R)-\log R.
\]

平均似然仍无偏，但最后取 log 后仍有 Jensen 偏差，只是目标不同。

结论：

- 作为 tiny test 的平滑代理目标，平均 log 有实用道理；
- 它不是“无偏 log likelihood”，也不与标准 MLE 完全等价；
- N、R 足够大且各候选的偏差近似小而稳定时，两者会接近；
- 正式报告应说明做法，并做 N、R、seed 稳定性检查；
- 若强调无偏似然性质，应在普通似然尺度组合重复，再用稳定 logsumexp 取 log。

## 110. “提前返回，不会走到打印”是什么意思？

objective 中：

    if not valid_params(p):
        return 1e100

return 立即结束本次函数。下面计算 elapsed 和 print 的代码不执行。因此 eval_counter 已加 1，但日志没有这一编号，可能看到 eval 0002 后直接 eval 0004。

## 111. NEW BEST 逻辑举例

初始 best=+inf。

- 第一次 obj=120：120<inf，best=120，打印 NEW BEST；
- 第二次 obj=130：不更好，best 仍 120，不打印；
- 第三次 obj=105：105<120，更新 best=105，打印 NEW BEST。

因为 obj 是负 loglik，obj 越小越好。

## 112. 随机种群全局最小化方法是什么？

不是只维护一个当前参数，而是维护 S 个分散候选；通过随机差分变异与交叉探索边界空间，并按目标值进行选择。“全局”指搜索范围和机制更广，不依赖单个初值附近的梯度；仍没有有限运行下找到真全局最优的保证。

## 113. popsize 是种群大小乘子

SciPy 中自由参数数为 d 时，默认种群大小约：

\[
S=\text{popsize}\times d
\]

（存在固定边界维度、初始化策略和最低规模等实现细节）。

本代码 d=2、popsize=3，名义 S=6。若估 5 个参数，则名义 S=15。popsize 越大覆盖更广、每代 PF 调用越多。

## 114. polish=False 和后面自己控制

differential_evolution 自带 polish 参数，True 时结束后自动调用局部优化。代码将它固定为 False，然后另写：

    if polish:
        minimize(..., method="L-BFGS-B")

这样能自定义局部方法、maxiter、ftol，并只在 POLISH_WITH_LBFGSB=True 时启用。

## 115. workers=1：串行计算

一次只在一个工作进程中评估一个候选，不并行。

- workers=1：简单、可复现、无进程通信开销；
- workers=-1：通常尝试使用所有 CPU 核，但要求 objective 可序列化，并会把 updating 改为 deferred 等。

此代码内部 PF 已很重，但盲目多进程也可能导致内存、随机数和 Spyder 环境问题。

## 116. L-BFGS-B 精修是什么？

差分进化先得到近似好点；L-BFGS-B 从该点出发，用局部梯度/有限差分信息寻找更低 objective。

“精修”意味着不再大范围探索，而是在附近提高小数精度。B 支持 log 参数边界；limited-memory 适合维数较大而不存完整 Hessian。

## 117. 为什么 PF 噪声让 L-BFGS-B 未必可靠？

若目标评价为：

\[
\widehat f(\theta)=f(\theta)+\varepsilon(\theta),
\]

有限差分梯度：

\[
\frac{\widehat f(\theta+h)-\widehat f(\theta)}h
\]

可能主要放大噪声差，而非真实斜率。

此外：

- exact 覆盖指示随参数/随机路径跳变；
- soft 虽平滑几何边界，但 Gillespie 接受/拒绝和事件次数仍会造成路径级不光滑；
- 重采样祖先也会离散变化。

所以 L-BFGS-B 可能错误判断方向或过早停止。固定随机数和增大 N 能改善，但不能自动保证平滑。

## 118. 描述性诊断是什么意思？

只描述当前数据特征，不进行正式显著性推断。

death_spatial_diagnostic 输出：

- T-zone 内外死亡数；
- 区域面积；
- 计数/面积密度；
- 密度比。

它没有给 p 值、置信区间，也没有控制隐藏状态和时间依赖。因此只能说“样本看起来怎样”，不能单凭它断言总体显著富集。

## 119. np.std(..., ddof=1) 为什么分母是 R-1？

样本均值：

\[
\bar x=\frac1R\sum_rx_r.
\]

样本方差无偏估计：

\[
s^2=\frac1{R-1}\sum_r(x_r-\bar x)^2.
\]

ddof=1 表示自由度减 1，分母 R-1；NumPy 默认 ddof=0 则分母 R，计算总体标准差形式。

## 120. 一次重复显示 0 及 return arr

R=1 时分母 R-1=0，不能从一个数估计随机波动。代码用条件表达式显示 0.0，避免 NaN/警告。

但 0 只是“没有足够重复来计算”，绝不能解释为 PF 没噪声。更清楚的输出应显示 “not estimable”。

return arr 把所有 loglik 数值交还调用者，之后可画直方图、算分位数或比较不同 N。

# 第四部分：剖面、输出、抽样设计与最终建议（121–160）

## 121. 看一维对数似然形状是什么意思？

固定其他参数，只改变一个参数 \(\lambda_{a,c}\)，计算：

\[
\ell(\lambda_{a,c})
\]

在多个点的值并作图/列表。可以看到：

- 是否有清楚单峰；
- 峰是否靠边界；
- 曲线是否很平（参数难识别）；
- 是否多峰；
- PF 噪声是否大于趋势。

## 122. 在线性 log 空间用 linspace 等分是什么意思？

代码：

\[
u_j=\operatorname{linspace}(\log0.005,\log0.5,M),
\qquad
\lambda_j=e^{u_j}.
\]

u 值等距，但原参数是等比例增长。

若只取 3 点：

\[
\log0.005,\log0.05,\log0.5
\]

对应原尺度 0.005、0.05、0.5，每次乘 10。

## 123. 为什么对数网格适合跨数量级的正参数？

线性网格从 0.005 到 0.5 的大部分点会集中在较大绝对值区间，对很小参数分辨不足。对数网格关注相对比例：

\[
0.005,\ 0.01,\ 0.02,\ 0.04,\ldots
\]

对强度、率和尺度参数通常更自然，因为 0.005 到 0.01 的两倍变化，可能和 0.25 到 0.5 的两倍变化同样重要。

## 124. 什么是剖面？为什么用同一 seed 更稳定？

**似然剖面**通常指：关注一个参数时，对其他参数固定或优化，然后查看似然随该参数的变化。本代码是简化的一维切片：其他参数固定在 true_params，并没有对它们重新优化，所以严格说更像 likelihood slice。

所有网格点使用同一 area_points 和 PF seed，让共同随机误差尽量抵消，曲线更少出现纯随机锯齿。但需换多组 seed 检查峰的位置是否稳定。

## 125. .6g 格式是什么意思？

Python 格式：

    f"{x:.6g}"

表示用 6 位有效数字显示，并根据大小自动选择普通小数或科学计数法。

例如：

- 0.12345678 → 0.123457；
- 12345678 → 1.23457e+07。

g 是 general format，不是固定 6 位小数。

## 126. <14、>12、>16 是什么意思？

字符串格式的字段宽度与对齐：

- <14：宽 14 个字符，左对齐；
- >12：宽 12，右对齐；
- >16：宽 16，右对齐。

例如 parameter 名左对齐，数字右对齐，打印成整齐表格。宽度不足时 Python 不截断内容，会自动超过指定宽度。

## 127. getattr 是什么意思？

动态按字符串读取对象属性：

    getattr(p, "lambda_d")

等价于：

    p.lambda_d

优势是 key 来自循环，无法预先写死字段名。若属性不存在且没提供默认值，会抛 AttributeError。

## 128. sim["final_time"] 是什么意思？

sim 是字典，["final_time"] 用键读取对应值。

模拟器返回：

    "final_time": np.array([t])

所以 sim["final_time"] 是长度 1 数组，[0] 再取其中的 t：

    float(sim["final_time"][0])

## 129. np.savetxt 解释

把二维数组保存为文本文件：

    np.savetxt(
        "simulated_death_events.csv",
        deaths,
        delimiter=",",
        header="x,y,t",
        comments=""
    )

- 文件名：写入当前工作目录；
- deaths：每行数据；
- delimiter=","：逗号分隔；
- header：首行列名；
- comments=""：不在表头前添加默认 #。

结果类似：

    x,y,t
    1.2,4.5,0.31
    ...

## 130. 为什么固定时间窗的点过程似然更直接？

固定 T 时实验设计预先确定：

> 观察 [0,T] 内所有事件。

似然明确包含：

\[
\exp\left(-\int_0^T h_sds\right)
\prod_{k:s_k\le T}\lambda(s_k).
\]

最后事件到 T 的无事件区间也是数据。

若在第 n 个死亡停止，终点 \(T_n\) 是数据的一部分。此时可能使用：

- 前 n 个到达的联合密度；
- 条件于 \(N(T)=n\) 的似然；
- 条件于停止时间 \(T_n\)；
- 停止规则下的完整似然。

这些不是同一个对象。当前代码令 T_end=第 8 次死亡时刻，最后无死亡区间长度为 0，更接近前 8 个事件的到达密度；若论文把它说成预先固定观察窗似然，就不严谨。

## 131. 空间诊断是什么意思？

检查死亡位置在固定 T-zone 内外是否表现不同。代码计算密度比：

\[
\frac{n_T/|T|}{n_{\mathrm{out}}/|W\setminus T|}.
\]

- >1：样本中 T-zone 每单位面积死亡更多；
- =1：相同；
- <1：更少。

它只诊断结果，不解释因果，也不等于模型参数估计。

## 132. 诊断积分点是什么意思？

diagnostic_area_points 是专门在真参数与估计参数重新计算 loglik 时使用的固定空间积分点。它们使 ll_true 与 ll_est 采用同一个数值积分规则，便于公平比较。

名称 diagnostic 说明它们用于最后比较；数学性质与 fit_parameters 内的 area_points 相同。

## 133. 优化前 PF 噪声诊断是什么意思？

在开始搜索参数前，固定真参数，多次换 PF seed 计算 loglik。目的是回答：

> 连参数都不变，仅粒子随机性就会让 loglik 波动多少？

若标准差 10，而不同参数 loglik 只差 2，优化器几乎无法可靠排序，应先加粒子。

## 134. 基准参数是什么意思？

base_params 是一个完整参数模板。优化器只替换 keys 指定字段，其余字段保持基准值。

仿真实验用 true_params 作 base，看起来方便，但真实数据没有真参数。实际需要：

- 外部实验给定；
- 单独校准；
- 合理初值固定；
- 或逐步扩大 ESTIMATE_KEYS 联合估计。

## 135. “估计参数比真参数拟合得更好”是什么意思？

若：

\[
\ell(\widehat\theta)>\ell(\theta_{\rm true}),
\]

说明对当前有限数据和当前 PF 随机评估，估计参数给观察数据更高密度。

MLE 的定义正是找样本似然最大点，因此估计值优于真值的样本似然很正常；真值是生成分布参数，不保证对每个随机样本都恰好最大。

## 136. 为什么有限样本 MLE 不等于真值？PF 噪声又怎样影响？

简单例子：8 次 Bernoulli，真 \(p=0.5\)，恰好观测 6 次成功，则 MLE：

\[
\widehat p=6/8=0.75,
\]

不等于 0.5。样本增大后才通常趋近真值。

本模型还有隐藏路径与 Monte Carlo 误差：

\[
\widehat\ell_{\rm PF}(\theta)
=\ell(\theta)+\varepsilon_{\rm PF}(\theta).
\]

优化器可能选到真实样本波动造成的峰，也可能选到 \(\varepsilon_{\rm PF}\) 偶然较高的候选。固定/配对 seed 能减比较噪声，不能消除有限样本差。

## 137. 为什么要在 estimated_params 处重复 PF？

计算：

\[
\Delta=\widehat\ell(\widehat\theta)
-\widehat\ell(\theta_{\rm true}).
\]

若 \(\Delta=3\)，但每处 PF 标准差约 8，就不能认真宣称估计参数明显更好；差异可能完全是 Monte Carlo 波动。

重复诊断帮助把“参数差异信号”和“PF 噪声”比较。

## 138. 打印完整 ModelParams 是什么意思？

estimated_params 总有八个字段。若只估 lambda_a_T、lambda_a_c：

- 这两个是优化结果；
- 其余六个只是从 base_params 原样带过来。

打印完整对象方便确认最终计算使用了哪些固定值，但不能把全部八个都称为“估计出来的参数”。

## 139. 为什么 best_loglik 与 ll_est 可能不同？

best_loglik 来自优化过程中 seed=PF_SEED（及重复种子）；ll_est 在主程序中用 seed=PF_SEED+999 重新评价。

PF 是随机估计：

\[
\widehat\ell(\theta;u_1)
\ne
\widehat\ell(\theta;u_2)
\]

很正常。二者差很多说明粒子数不足或权重退化严重；不是代码一定出错。

## 140. 逐渐减小 SOFT_SIGMA 再 exact 是什么意思？

SOFT_SIGMA 是问题 19 的边界平滑宽度。

建议 continuation：

1. sigma=0.2，先保证优化能工作；
2. sigma=0.1；
3. sigma=0.05；
4. 最后尝试 exact。

每次以上一步估计为参考并增加粒子，观察参数是否稳定。sigma 直接跳很小可能立即权重坍塌。

## 141. 为什么死亡数据可能不能同时识别所有 caspase/ERK 参数？

不同参数组合可能产生相似死亡分布，称为不可识别或弱识别。

例如：

- 更高激活率但更小激活半径；
- 更高死亡率但更强 ERK 保护；
- 更频繁激活但更短寿命；

都可能产生相似死亡数和空间图案。只看到死亡，看不到 active 与 ERK，就难区分背后机制。

一开始只估 2 个最有信息的参数，其他固定；再看剖面和恢复实验决定能否增加参数。否则优化可能有长脊、多峰、边界估计。

## 142. 为什么不可能粒子得到极小权重而不是真零？

death_event_intensity 在不满足硬几何条件时返回：

\[
\varepsilon=10^{-12},
\]

而不是 0。因此：

\[
G_i=e^{-\int h}\varepsilon>0,
\quad
\widetilde w_i=w_iG_i>0.
\]

它会非常小，但数学上不是零。这样避免 math.log(0)，代价是给原模型中不可能路径加入微小可能性。

## 143. 完全 exact 为什么要允许 \(-\infty\) 并处理全体坍塌？

若事件强度为 0：

\[
\log\lambda=\log0=-\infty.
\]

在 log 域这是合理的扩展实数：

- 某些粒子 -inf：它们普通权重为 0，可由 logsumexp 忽略；
- 所有粒子 -inf：归一化常数为 0，后验粒子近似不存在，说明 proposal 没命中观测支持集。

此时不能简单继续；需要：

- 返回整个候选似然 0；
- 增大粒子数；
- 使用观测引导 proposal/辅助粒子滤波；
- 或重新设计连续观测误差模型。

加 epsilon 只是绕开算法坍塌，并非解决支持集不匹配。

## 144. 固定第 8 次死亡停止与固定时间抽样设计

固定时间：

> 无论发生几次，都观察到预定 T。

固定事件数：

> 无论花多久，都等到第 8 次事件。

后者必然观测 8 个死亡，所以“死亡数为 8”本身不再提供参数信息；信息主要在到达时间 \(T_8\)、间隔和位置。

“条件于 n”是把事件数视为已知条件；“条件于停止时间”又会改变密度；“使用停止时刻似然”则把 \(T_n\) 作为随机观测。论文必须说清楚，否则公式中最后 survival 项和计数信息的含义可能错。

## 145. 为什么 8 次死亡不能可靠识别？需要多少死亡？

8 个死亡只提供 8 组位置/时间，而隐藏路径维度很高，参数效应又互相补偿。没有通用的“每参数 10 个事件”规则适用于这种隐藏点过程。

实用分级（仅启发，不是定理）：

- 8：只做单元测试；
- 20–60：调试、粗略趋势；
- 200–500：可开始评估两个参数的恢复稳定性；
- 1000 或更多：更适合多参数正式 simulation study，但仍不保证八参数可识别。

最可靠的决定方法：

1. 用真参数分别模拟 n=60、200、500、1000；
2. 每个 n 至少多组独立数据；
3. 拟合后比较偏差、RMSE、边界命中、剖面宽度；
4. 增加 n 后结果不再明显变化，才说明信息可能足够。

你的正式模拟本来已有 1000 deaths × 5 replicates；若计算允许，参数恢复应逐步向 200/500/1000 扩展，而不是用 8 得结论。

## 146. 固定空间积分点是什么？

一次生成 \(U_1,\ldots,U_M\)，之后对所有粒子、所有参数、所有诊断重复使用。它们是 Monte Carlo quadrature nodes，不随状态重新抽样。

优点：比较方差小、结果可复现。缺点：优化器可能适应这一个有限网格；最终应换 AREA_SEED 或增大 M 验证。

## 147. eval_counter 字典

    eval_counter = {"n":0, "best":np.inf}

- "n"：objective 已被调用次数；
- "best"：目前最小 obj。

字典可在内部 objective 中原地修改，不需 nonlocal：

    eval_counter["n"] += 1
    eval_counter["best"] = float(obj)

## 148. unpack 和 invalid penalty

    p = unpack_log_params(log_vec,base_params,keys)

把优化器的 log 参数转回完整正参数 p。

    if not valid_params(p):
        return 1e100

若有非有限、非正或违反：

\[
\lambda_{a,c}\le\lambda_{a,T}\le\lambda_{a,1},
\]

立即返回巨大目标，拒绝候选。

## 149. vals = ", ".join(...) 解释

内部生成器：

    f"{k}={getattr(p,k):.5g}" for k in keys

对每个参数名产生字符串，例如：

    "lambda_a_T=0.50000"
    "lambda_a_c=0.050000"

getattr 按名字取值，.5g 用 5 位有效数字。

    ", ".join(...)

用逗号和空格连接：

    "lambda_a_T=0.5, lambda_a_c=0.05"

## 150. eval print 逐项解释

    eval {n:04d}

编号至少 4 位，不足补 0，如 7→0007。

    obj={obj:.4f}

目标保留 4 位小数。

    loglik={-obj:.4f}

由于 obj 是负平均 loglik，再取负显示原方向。

    time={elapsed:.2f}s

本次耗时保留 2 位小数。

    {vals}{best_mark}

显示参数；若刷新最佳，再加 NEW BEST。

    flush=True

立即把缓冲输出显示出来，长任务中不必等缓冲区满。

## 151. if polish 是什么意思？

polish 是 bool：

- True：执行其缩进代码，运行 L-BFGS-B；
- False：跳过。

默认来自 POLISH_WITH_LBFGSB=False。

## 152. minimize 参数解释

    minimize(objective, best_x, ...)

- objective：要最小化的函数；
- best_x：差分进化最佳 log 参数，作为局部起点；
- method="L-BFGS-B"：有边界拟牛顿法；
- bounds=bounds：log 参数上下界；
- options["maxiter"]=30：最多 30 个局部迭代；
- options["ftol"]=1e-3：目标函数相对改善足够小时停止。

返回 OptimizeResult，重要字段：

- x：局部最佳点；
- fun：局部最小目标；
- success/message：停止状态。

本代码没有检查 success 和 message，正式使用最好打印检查。

## 153. 只在局部结果更好时替换

    if result_local.fun < best_obj:

局部优化目标小于差分进化目标，说明改善。

    best_x = result_local.x

保存新 log 参数。

    best_obj = float(result_local.fun)

保存新目标。

若局部结果更差或噪声使其变差，就保留差分进化结果。

## 154. 一维 profile 文档字符串翻译

翻译：

> 可选的一维剖面诊断：改变 lambda_a_c，同时保持 lambda_a_T 固定。

它查看 lambda_a_c 方向的似然变化。其余所有参数也固定，因此严格说是固定参数切片，不是每个 lambda_a_c 下重新优化 nuisance parameters 的完整 profile likelihood。

## 155. best_lc=None 和 best_ll=-np.inf

- best_lc 尚未找到任何最佳网格值，所以用 None；
- best_ll 从负无穷开始，因此第一个有限 ll 一定更大并被记录。

如果所有网格点无效，best_lc 保持 None，最后 .6g 格式化会报错；当前网格通常有有效点。

## 156. 遍历网格与 replace

    for lc in grid:

逐个取候选 lambda_a_c。

    p_test = replace(true_params,lambda_a_c=float(lc))

复制 true_params，只替换 lambda_a_c；原 true_params 不变。

## 157. 保存网格最佳值

    if ll > best_ll:

当前 loglik 比历史最大值高。

    best_ll = ll
    best_lc = float(lc)

同时保存最高似然和对应参数。例：先 -100，再 -95，则更新；之后 -110 不更新。

## 158. 固定 quadrature points 注释翻译

翻译：

> 使用一组固定的求积点进行诊断，并使不同对数似然调用之间具有可比性。

quadrature points 是数值积分点。固定同一组，使 ll_true 和 ll_est 的空间积分误差尽量共同，而不是各自碰到不同随机网格。

## 159. diagnostic_area_points 代码

    rng_area.uniform(0.0,Lx,M)

生成 M 个 x。

    rng_area.uniform(0.0,Ly,M)

生成 M 个 y。

    np.column_stack([...])

拼成 \((M,2)\) 的固定诊断坐标。AREA_SEED 相同且 M 相同的话，它与 fit_parameters 内生成的点坐标相同。

## 160. Notes 全文翻译与解释

### 原第 1 条

翻译：

> 如果 PF 噪声的标准差相对于“估计参数与真参数的 loglik 差”很大，那么在解释 MLE 前，应增加 N_PARTICLES 和 PF_REPLICATES。

解释：若差值 2、噪声标准差 10，无法确认差异来自参数。

### 第 2 条

翻译：

> 推荐固定时间模拟，以获得解释更清晰的点过程似然。

解释见问题 130、144：预先固定 T 时观察机制和最后无事件项明确。

### 第 3 条

翻译：

> soft 版本工作正常后，先尝试更小的 SOFT_SIGMA，然后再设置 LIKELIHOOD_MODE="exact"。

解释：逐步逼近硬模型，避免立刻坍塌；每步都应提高粒子数并检查稳定性。

### 第 4 条

翻译：

> 仅死亡数据可能无法同时识别所有 caspase 和 ERK 参数；先估计一个较小参数子集，再逐步扩大 ESTIMATE_KEYS。

解释：死亡是多个隐藏机制的间接结果，不同参数组合可能产生类似数据。扩大参数集前要用剖面、参数恢复和多初值验证识别性。

# 最重要的综合结论

1. 当前文件是 tiny test，不是可直接用于论文结论的正式配置。
2. soft 模式缓解支持集不匹配，但改变了原始硬模型。
3. exact 模式中的 \(10^{-12}\) 又使其并非严格 exact。
4. PF 的似然估计是随机的，必须报告 seed/N/R 稳定性。
5. 平均 loglik 是实用代理目标，但不是无偏 log likelihood。
6. 8 个死亡只能检查代码；所需样本量应通过参数恢复实验决定。
7. 固定时间与固定第 n 个事件是不同观察设计，论文必须明确。

# 网页与官方资料

- [Python 内置常量 None](https://docs.python.org/3/library/constants.html#None)
- [Python 内置函数：all、enumerate、getattr、zip](https://docs.python.org/3/library/functions.html)
- [Python dataclasses：frozen 与 replace](https://docs.python.org/3/library/dataclasses.html)
- [Python typing 与 Sequence](https://docs.python.org/3/library/typing.html)
- [NumPy ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html)
- [NumPy isfinite](https://numpy.org/doc/stable/reference/generated/numpy.isfinite.html)
- [NumPy clip](https://numpy.org/doc/stable/reference/generated/numpy.clip.html)
- [NumPy full](https://numpy.org/doc/stable/reference/generated/numpy.full.html)
- [NumPy column_stack](https://numpy.org/doc/stable/reference/generated/numpy.column_stack.html)
- [NumPy cumsum](https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html)
- [NumPy searchsorted](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html)
- [NumPy argsort](https://numpy.org/doc/stable/reference/generated/numpy.argsort.html)
- [NumPy savetxt](https://numpy.org/doc/stable/reference/generated/numpy.savetxt.html)
- [NumPy exponential：参数是 scale=率的倒数](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.exponential.html)
- [SciPy optimize 总览](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [SciPy differential_evolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html)
- [SciPy minimize](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)
- [SciPy L-BFGS-B](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html)
- [Doucet 与 Johansen：粒子滤波与平滑教程](https://www.stats.ox.ac.uk/~doucet/doucet_johansen_tutorialPF2011.pdf)
- [Rasmussen：条件强度与点过程似然讲义](https://arxiv.org/pdf/1806.00221)
- [Gillespie 1977 原始随机模拟论文](https://www.cmor-faculty.rice.edu/~cox/gillespie.pdf)
- [Glasserman 与 Yao：公共随机数方法](https://business.columbia.edu/sites/default/files-efs/pubfiles/4261/glasserman_yao_guidelines.pdf)
- [van Handel：HMM 与马尔可夫性质讲义](https://web.math.princeton.edu/~rvan/orf557/hmm080728.pdf)
