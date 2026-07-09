# pf_mle_caspase_erk_DEBUG_STABLE(1).py 逐行中文解释

这份文件把原始 Python 代码按行号拆开，并给每一行加中文解释。适合你一边打开原代码，一边对照理解。

## 先看整体逻辑

1. 第 1 部分设置全局参数：空间窗口、粒子数、重采样方法、优化次数。

2. 第 2 部分定义模型参数 `ModelParams` 和粒子状态 `ParticleState`。

3. 第 3 部分是几何函数：判断点在不在 T-zone、圆盘并集、active/unprotected 区域。

4. 第 4 部分用 Gillespie 模型模拟合成死亡事件。

5. 第 5 部分是核心：给定观测死亡事件，用粒子滤波估计 log-likelihood。

6. 第 6 部分用 `differential_evolution` 优化参数。

7. 第 7 部分是诊断：死亡点空间分布、PF 噪声、似然剖面。

8. 第 8 部分 `main()` 串起全部流程：模拟 → 诊断 → 优化 → 输出结果。


---

## 逐行解释


### 第 1–50 行

**L0001**

```python
"""
```

解释：三引号：开始或结束一段多行说明文字/文档字符串，Python 会把它当作字符串。

**L0002**

```python
Particle-filter maximum likelihood for an observation-driven caspase--ERK
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0003**

```python
point-process model.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0004**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0005**

```python
This script is written to match the user's Gillespie simulator structure:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0006**

```python
    hidden caspase activation V^a_t;
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0007**

```python
    observed death events Y^d = {(y_i^d, s_i^d)};
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0008**

```python
    ERK protection V^p_t triggered after observed deaths.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0009**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0010**

```python
Key modelling correction:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0011**

```python
    The particle filter does NOT treat X_t=(V^a_t,V^p_t) as an autonomous HMM.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0012**

```python
    The rigorous augmented state is
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0013**

```python
        Z_t = (V^a_t, V^p_t, V^d_{0:t}),
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0014**

```python
    where V^d_{0:t} is the observed death history. In code, V^d is common to
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0015**

```python
    all particles, so each particle stores only (V^a_t,V^p_t), while transitions
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0016**

```python
    and likelihood are computed conditionally on the observed death history.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0017**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0018**

```python
What the script does:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0019**

```python
    1. Simulate synthetic death-event data from the original Gillespie model.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0020**

```python
    2. Estimate selected parameters by maximizing a particle-filter likelihood.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0021**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0022**

```python
Important practical warning:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0023**

```python
    With the exact hard indicator death intensity,
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0024**

```python
        lambda_d * 1{x in A(Va)} * 1{x not in A(Vp)},
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0025**

```python
    a bootstrap particle filter can suffer severe weight collapse because a
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0026**

```python
    randomly simulated hidden activation field often does not cover the exact
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0027**

```python
    observed death location. For debugging/inference, this script includes
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0028**

```python
    LIKELIHOOD_MODE = "soft", a smooth approximation to the hard indicator.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0029**

```python
    Set LIKELIHOOD_MODE = "exact" when you want the literal model.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0030**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0031**

```python
Dependencies:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0032**

```python
    numpy, scipy
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0033**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0034**

```python
Run:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0035**

```python
    python pf_mle_caspase_erk_observation_driven.py
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0036**

```python
"""
```

解释：三引号：开始或结束一段多行说明文字/文档字符串，Python 会把它当作字符串。

**L0037**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0038**

```python
from __future__ import annotations
```

解释：启用较新的类型注解行为，让类型提示可以延迟解析，减少前向引用问题。

**L0039**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0040**

```python
from dataclasses import dataclass, replace
```

解释：@dataclass 用来自动生成类的初始化等方法；replace 用来基于旧参数对象生成改过字段的新对象。

**L0041**

```python
from typing import Dict, Iterable, List, Sequence, Tuple
```

解释：导入类型提示工具，例如 Dict/List/Sequence/Tuple，让函数签名更清楚。

**L0042**

```python
import math
```

解释：导入 Python 标准数学库，用于 log、exp、sqrt 等标量数学函数。

**L0043**

```python
import time
```

解释：导入计时库，用来统计一次似然评估花了多久。

**L0044**

```python
import numpy as np
```

解释：导入 NumPy 并简称 np；数组、随机数、向量化计算主要靠它。

**L0045**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0046**

```python
try:
```

解释：开始 try 块：尝试执行下面的导入，如果失败就进入 except。

**L0047**

```python
    from scipy.optimize import differential_evolution, minimize
```

解释：从 SciPy 优化模块导入差分进化和局部最小化算法，用于参数估计。

**L0048**

```python
except Exception as exc:  # pragma: no cover
```

解释：如果上面的 SciPy 导入失败，就捕获异常并命名为 exc。

**L0049**

```python
    raise ImportError("This script needs scipy: pip install scipy") from exc
```

解释：主动报错：告诉用户需要安装 scipy；from exc 会保留原始错误信息。

**L0050**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。


### 第 51–100 行

**L0051**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0052**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0053**

```python
# 1. Global configuration for a first runnable demo
```

解释：全局配置：控制空间大小、粒子数、优化设置等。

**L0054**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0055**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0056**

```python
# Spatial domain W = [0,Lx] x [0,Ly]
```

解释：注释：Spatial domain W = [0,Lx] x [0,Ly]。

**L0057**

```python
Lx = 10.0
```

解释：空间窗口 W 在 x 方向的长度。

**L0058**

```python
Ly = 10.0
```

解释：空间窗口 W 在 y 方向的长度。

**L0059**

```python
AREA_W = Lx * Ly
```

解释：空间窗口 W 的面积，即 Lx × Ly。

**L0060**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0061**

```python
# Fixed T-zone definition, copied from the uploaded simulator.
```

解释：注释：Fixed T-zone definition, copied from the uploaded simulator.。

**L0062**

```python
x1 = Lx / 3.0
```

解释：T-zone 边界的第一个 x 坐标，等于 Lx/3。

**L0063**

```python
x2 = 2.0 * Lx / 3.0
```

解释：T-zone 边界的第二个 x 坐标，等于 2Lx/3。

**L0064**

```python
y1 = Ly / 3.0
```

解释：T-zone 边界的第一个 y 坐标，等于 Ly/3。

**L0065**

```python
y2 = 2.0 * Ly / 3.0
```

解释：T-zone 边界的第二个 y 坐标，等于 2Ly/3。

**L0066**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0067**

```python
# Recommended simulation mode for likelihood inference:
```

解释：注释：Recommended simulation mode for 似然 inference:。

**L0068**

```python
#   fixed-time window is cleaner than stopping exactly at the 60th death.
```

解释：注释：fixed-time window is cleaner than stopping exactly at the 60th death.。

**L0069**

```python
#   If this is too slow, set USE_FIXED_TIME_WINDOW=False.
```

解释：注释：If this is too slow, set USE_FIXED_TIME_WINDOW=False.。

**L0070**

```python
USE_FIXED_TIME_WINDOW = True
```

解释：是否使用固定观察时间窗口；True 表示模拟到 T_MAX。

**L0071**

```python
T_MAX = 2.0
```

解释：固定观察窗口的终止时间。

**L0072**

```python
TARGET_DEATHS = None if USE_FIXED_TIME_WINDOW else 8
```

解释：如果不用固定时间窗口，就停止在目标死亡数；这里为 None。

**L0073**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0074**

```python
# Particle filter settings.
```

解释：注释：Particle filter settings.。

**L0075**

```python
# Start here; increase N_PARTICLES / PF_REPLICATES for final results.
```

解释：注释：Start here; increase N_PARTICLES / PF_REPLICATES for final results.。

**L0076**

```python
N_PARTICLES = 30
```

解释：粒子滤波中的粒子数量 N。越大越准但越慢。

**L0077**

```python
AREA_MC_POINTS = 100
```

解释：用来近似空间面积积分的 Monte Carlo 点数。

**L0078**

```python
RESAMPLE_THRESHOLD = 0.75  # Alg. 7 in the notes uses N_eff / N <= 0.75
```

解释：重采样阈值；当有效样本量比例低于这个数就重采样。

**L0079**

```python
RESAMPLE_METHOD = "residual_systematic"  # multinomial, systematic, stratified, residual_multinomial, residual_systematic
```

解释：粒子重采样/redistribution 的方法。

**L0080**

```python
PF_REPLICATES = 3
```

解释：同一个参数下重复粒子滤波的次数，用来降低似然估计噪声。

**L0081**

```python
PF_SEED = 20260709
```

解释：粒子滤波随机种子。

**L0082**

```python
AREA_SEED = 20260710
```

解释：面积 Monte Carlo 点的随机种子。

**L0083**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0084**

```python
# "exact" uses hard indicators. "soft" uses a smooth approximation.
```

解释：注释："exact" uses hard indicators. "soft" uses a smooth approximation.。

**L0085**

```python
# A smaller SOFT_SIGMA is closer to the exact model but can be noisier.
```

解释：注释：A smaller SOFT_SIGMA is closer to the exact model but can be noisier.。

**L0086**

```python
LIKELIHOOD_MODE = "soft"  # "soft" or "exact"
```

解释：似然计算模式：soft 是平滑近似，exact 是硬指标函数。

**L0087**

```python
SOFT_SIGMA = 0.10
```

解释：soft 模式下 sigmoid 平滑宽度；越小越接近 hard indicator。

**L0088**

```python
MIN_EVENT_INTENSITY = 1e-12
```

解释：事件强度的下界，避免 log(0)。

**L0089**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0090**

```python
# Optimization settings. Increase maxiter/popsize for better inference.
```

解释：注释：Optimization settings. Increase maxiter/popsize for better inference.。

**L0091**

```python
OPT_MAXITER = 3
```

解释：差分进化优化的最大迭代数。

**L0092**

```python
OPT_POPSIZE = 4
```

解释：差分进化种群大小参数。

**L0093**

```python
POLISH_WITH_LBFGSB = False
```

解释：是否在差分进化之后用 L-BFGS-B 局部优化精修。

**L0094**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0095**

```python
# Diagnostics. They cost extra time but are very useful for debugging inference.
```

解释：注释：Diagnostics. They cost extra time but are very useful for debugging inference.。

**L0096**

```python
RUN_DEATH_SPATIAL_DIAGNOSTIC = True
```

解释：是否打印死亡点在 T-zone 内外的空间诊断。

**L0097**

```python
RUN_PF_NOISE_DIAGNOSTIC = True
```

解释：是否运行粒子滤波噪声诊断。

**L0098**

```python
PF_NOISE_REPEATS = 5
```

解释：粒子滤波噪声诊断重复次数。

**L0099**

```python
RUN_LIKELIHOOD_PROFILE = False
```

解释：是否画/打印一维似然剖面诊断。

**L0100**

```python
PROFILE_GRID_SIZE = 15
```

解释：似然剖面网格点数量。


### 第 101–150 行

**L0101**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0102**

```python
# Estimate a subset first. Do not estimate all parameters at once at the beginning.
```

解释：注释：Estimate a subset first. Do not estimate all parameters at once at the beginning.。

**L0103**

```python
# Start with identifiable parameters. Do NOT estimate all five at first.
```

解释：注释：Start with identifiable parameters. Do NOT estimate all five at first.。

**L0104**

```python
# After this works, try adding "lambda_d", then radius/lifetime parameters one by one.
```

解释：注释：After this works, try adding "λ_d", then radius/lifetime parameters one by one.。

**L0105**

```python
ESTIMATE_KEYS = (
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0106**

```python
    "lambda_a_T",
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0107**

```python
    "lambda_a_c",
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0108**

```python
)
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0109**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0110**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0111**

```python
# 2. Parameters and state
```

解释：参数和状态：定义模型参数对象与粒子状态。

**L0112**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0113**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0114**

```python
@dataclass(frozen=True)
```

解释：装饰器：把下面的类变成 dataclass；frozen=True 表示对象创建后字段不能直接修改。

**L0115**

```python
class ModelParams:
```

解释：定义 ModelParams 类：集中保存模型的所有参数。

**L0116**

```python
    # Caspase activation intensities
```

解释：注释：Caspase activation intensities。

**L0117**

```python
    lambda_a_1: float = 5.00   # dominating intensity and active-zone intensity
```

解释：caspase activation 的 dominating intensity，也是 active-zone 内强度上界。

**L0118**

```python
    lambda_a_T: float = 0.50   # background activation intensity inside T-zone
```

解释：T-zone 内背景 activation 强度。

**L0119**

```python
    lambda_a_c: float = 0.05   # background activation intensity outside T-zone
```

解释：T-zone 外背景 activation 强度。

**L0120**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0121**

```python
    # Death intensity on active and unprotected region
```

解释：注释：Death intensity on active and unprotected region。

**L0122**

```python
    lambda_d: float = 1.00
```

解释：死亡事件强度系数。

**L0123**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0124**

```python
    # Activation mark/lifetime parameters
```

解释：注释：Activation mark/lifetime parameters。

**L0125**

```python
    beta_a_R: float = 2.50     # R^a ~ Exp(beta_a_R)
```

解释：activation 圆盘半径的指数分布 rate。

**L0126**

```python
    beta_a_T: float = 1.20     # active-center expiration rate
```

解释：activation center 的过期 rate。

**L0127**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0128**

```python
    # ERK mark/lifetime parameters
```

解释：注释：ERK mark/lifetime parameters。

**L0129**

```python
    beta_d_R: float = 2.00     # R^d ~ Exp(beta_d_R)
```

解释：ERK 保护圆盘半径的指数分布 rate。

**L0130**

```python
    beta_d_T: float = 0.80     # ERK-zone expiration rate
```

解释：ERK 保护区域的过期 rate。

**L0131**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0132**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0133**

```python
@dataclass
```

解释：装饰器：把下面的类变成 dataclass，自动生成 __init__ 等方法。

**L0134**

```python
class ParticleState:
```

解释：定义 ParticleState 类：保存单个粒子的隐藏状态 active 和 erk。

**L0135**

```python
    # Each list contains tuples (x,y,r)
```

解释：注释：Each list contains tuples (x,y,r)。

**L0136**

```python
    active: List[Tuple[float, float, float]]
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0137**

```python
    erk: List[Tuple[float, float, float]]
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0138**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0139**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0140**

```python
def clone_state(st: ParticleState) -> ParticleState:
```

解释：定义函数：复制一个粒子状态，避免重采样后多个粒子共享同一个 list。

**L0141**

```python
    return ParticleState(active=list(st.active), erk=list(st.erk))
```

解释：返回结果给调用这个函数的地方。

**L0142**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0143**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0144**

```python
def valid_params(p: ModelParams) -> bool:
```

解释：定义函数：检查参数是否合法：有限、正数，并满足 lambda_a_c <= lambda_a_T <= lambda_a_1。

**L0145**

```python
    vals = [
```

解释：把参数值收集成列表，方便统一检查。

**L0146**

```python
        p.lambda_a_1, p.lambda_a_T, p.lambda_a_c, p.lambda_d,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0147**

```python
        p.beta_a_R, p.beta_a_T, p.beta_d_R, p.beta_d_T,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0148**

```python
    ]
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0149**

```python
    if not all(np.isfinite(vals)) or not all(v > 0 for v in vals):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0150**

```python
        return False
```

解释：返回结果给调用这个函数的地方。


### 第 151–200 行

**L0151**

```python
    return p.lambda_a_c <= p.lambda_a_T <= p.lambda_a_1
```

解释：返回结果给调用这个函数的地方。

**L0152**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0153**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0154**

```python
# Bounds for direct positive parameters. Optimizer works in log-space.
```

解释：注释：Bounds for direct positive parameters. Optimizer works in log-space.。

**L0155**

```python
PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {
```

解释：定义参数取值范围字典；后面优化时会把这些上下界取 log。

**L0156**

```python
    "lambda_a_1": (0.2, 12.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0157**

```python
    # Background intensities. Bounds are intentionally moderate for stable first runs.
```

解释：注释：Background intensities. Bounds are intentionally moderate for stable first runs.。

**L0158**

```python
    "lambda_a_T": (0.02, 2.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0159**

```python
    "lambda_a_c": (0.002, 0.8),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0160**

```python
    "lambda_d": (0.05, 5.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0161**

```python
    "beta_a_R": (0.2, 8.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0162**

```python
    "beta_a_T": (0.05, 5.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0163**

```python
    "beta_d_R": (0.2, 8.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0164**

```python
    "beta_d_T": (0.05, 5.0),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0165**

```python
}
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0166**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0167**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0168**

```python
def unpack_log_params(log_vec: Sequence[float], base: ModelParams, keys: Sequence[str]) -> ModelParams:
```

解释：定义函数：把优化器给出的 log 参数向量转回真正参数，并替换到 ModelParams 里。

**L0169**

```python
    p = base
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0170**

```python
    for key, log_value in zip(keys, log_vec):
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0171**

```python
        p = replace(p, **{key: float(np.exp(log_value))})
```

解释：ParticleState 的字段 p，保存粒子状态的一部分。

**L0172**

```python
    return p
```

解释：返回结果给调用这个函数的地方。

**L0173**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0174**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0175**

```python
def pack_log_params(p: ModelParams, keys: Sequence[str]) -> np.ndarray:
```

解释：定义函数：把参数对象中的指定参数取 log，打包成 NumPy 数组。

**L0176**

```python
    return np.array([math.log(getattr(p, key)) for key in keys], dtype=float)
```

解释：返回结果给调用这个函数的地方。

**L0177**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0178**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0179**

```python
def log_bounds(keys: Sequence[str]) -> List[Tuple[float, float]]:
```

解释：定义函数：把普通参数边界转换成 log-space 边界。

**L0180**

```python
    return [(math.log(PARAM_BOUNDS[k][0]), math.log(PARAM_BOUNDS[k][1])) for k in keys]
```

解释：返回结果给调用这个函数的地方。

**L0181**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0182**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0183**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0184**

```python
# 3. Geometry helpers
```

解释：几何辅助函数：判断点是否在 T-zone、圆盘并集、active/unprotected 区域。

**L0185**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0186**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0187**

```python
def is_inside_T_zone(x: float, y: float) -> bool:
```

解释：定义函数：判断空间点 (x,y) 是否在固定 T-zone 里。

**L0188**

```python
    inside_middle_column = (x1 <= x <= x2) and (0.0 <= y <= Ly)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0189**

```python
    inside_left_arm = (0.0 <= x <= x1) and (y1 <= y <= y2)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0190**

```python
    return inside_middle_column or inside_left_arm
```

解释：返回结果给调用这个函数的地方。

**L0191**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0192**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0193**

```python
def inside_union_exact(x: float, y: float, discs: Sequence[Tuple[float, float, float]]) -> bool:
```

解释：定义函数：判断点是否落在若干圆盘的并集里。

**L0194**

```python
    for cx, cy, r in discs:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0195**

```python
        if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0196**

```python
            return True
```

解释：返回结果给调用这个函数的地方。

**L0197**

```python
    return False
```

解释：返回结果给调用这个函数的地方。

**L0198**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0199**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0200**

```python
def local_activation_intensity(x: float, y: float, st: ParticleState, p: ModelParams) -> float:
```

解释：定义函数：根据当前位置是否在 active 圆盘/T-zone/外部，返回 activation intensity。


### 第 201–250 行

**L0201**

```python
    if inside_union_exact(x, y, st.active):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0202**

```python
        return p.lambda_a_1
```

解释：返回结果给调用这个函数的地方。

**L0203**

```python
    if is_inside_T_zone(x, y):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0204**

```python
        return p.lambda_a_T
```

解释：返回结果给调用这个函数的地方。

**L0205**

```python
    return p.lambda_a_c
```

解释：返回结果给调用这个函数的地方。

**L0206**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0207**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0208**

```python
def _sigmoid_clipped(z: np.ndarray | float) -> np.ndarray | float:
```

解释：定义函数：安全计算 sigmoid，先把输入截断，避免 exp 溢出。

**L0209**

```python
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50.0, 50.0)))
```

解释：返回结果给调用这个函数的地方。

**L0210**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0211**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0212**

```python
def soft_union_probability_points(
```

解释：定义函数：对一批点计算“属于圆盘并集”的平滑概率。

**L0213**

```python
    points: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0214**

```python
    discs: Sequence[Tuple[float, float, float]],
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0215**

```python
    sigma: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0216**

```python
) -> np.ndarray:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0217**

```python
    """
```

解释：三引号：开始或结束一段多行说明文字/文档字符串，Python 会把它当作字符串。

**L0218**

```python
    Smooth approximation of 1{x in union of discs}.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0219**

```python
    For one disc, use sigmoid((r - distance)/sigma).
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0220**

```python
    For a union, use the max boundary score over discs.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0221**

```python
    """
```

解释：三引号：开始或结束一段多行说明文字/文档字符串，Python 会把它当作字符串。

**L0222**

```python
    n = points.shape[0]
```

解释：数量变量，通常表示点数或粒子数。

**L0223**

```python
    if len(discs) == 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0224**

```python
        return np.zeros(n, dtype=float)
```

解释：返回结果给调用这个函数的地方。

**L0225**

```python
    scores = np.full(n, -1e9, dtype=float)
```

解释：每个点到所有圆盘边界的最大分数 r-distance；大于 0 越像在圆盘内。

**L0226**

```python
    px = points[:, 0]
```

解释：所有点的 x 坐标向量。

**L0227**

```python
    py = points[:, 1]
```

解释：所有点的 y 坐标向量。

**L0228**

```python
    for cx, cy, r in discs:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0229**

```python
        dist = np.sqrt((px - cx) ** 2 + (py - cy) ** 2)
```

解释：点到圆心的欧氏距离。

**L0230**

```python
        scores = np.maximum(scores, r - dist)
```

解释：每个点到所有圆盘边界的最大分数 r-distance；大于 0 越像在圆盘内。

**L0231**

```python
    return _sigmoid_clipped(scores / sigma)
```

解释：返回结果给调用这个函数的地方。

**L0232**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0233**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0234**

```python
def soft_union_probability_one(
```

解释：定义函数：对单个点计算“属于圆盘并集”的平滑概率。

**L0235**

```python
    x: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0236**

```python
    y: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0237**

```python
    discs: Sequence[Tuple[float, float, float]],
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0238**

```python
    sigma: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0239**

```python
) -> float:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0240**

```python
    if len(discs) == 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0241**

```python
        return 0.0
```

解释：返回结果给调用这个函数的地方。

**L0242**

```python
    best = -1e9
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0243**

```python
    for cx, cy, r in discs:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0244**

```python
        dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
```

解释：点到圆心的欧氏距离。

**L0245**

```python
        best = max(best, r - dist)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0246**

```python
    return float(_sigmoid_clipped(best / sigma))
```

解释：返回结果给调用这个函数的地方。

**L0247**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0248**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0249**

```python
def active_unprotected_area(
```

解释：定义函数：用固定 Monte Carlo 点近似 active 且未保护区域的面积。

**L0250**

```python
    st: ParticleState,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。


### 第 251–300 行

**L0251**

```python
    area_points: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0252**

```python
    mode: str = "exact",
```

解释：ParticleState 的字段 mode，保存粒子状态的一部分。

**L0253**

```python
    sigma: float = SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0254**

```python
) -> float:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0255**

```python
    r"""Approximate |A(Va) \ A(Vp)| by fixed Monte Carlo quadrature points."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0256**

```python
    if len(st.active) == 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0257**

```python
        return 0.0
```

解释：返回结果给调用这个函数的地方。

**L0258**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0259**

```python
    if mode == "exact":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0260**

```python
        active = np.zeros(area_points.shape[0], dtype=bool)
```

解释：该粒子当前保存的隐藏 activation 圆盘列表。

**L0261**

```python
        protected = np.zeros(area_points.shape[0], dtype=bool)
```

解释：创建全 0 数组；可作为布尔 mask 或数值初始化。

**L0262**

```python
        px = area_points[:, 0]
```

解释：所有点的 x 坐标向量。

**L0263**

```python
        py = area_points[:, 1]
```

解释：所有点的 y 坐标向量。

**L0264**

```python
        for cx, cy, r in st.active:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0265**

```python
            active |= (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0266**

```python
        for cx, cy, r in st.erk:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0267**

```python
            protected |= (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0268**

```python
        return AREA_W * float(np.mean(active & (~protected)))
```

解释：返回结果给调用这个函数的地方。

**L0269**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0270**

```python
    if mode == "soft":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0271**

```python
        p_active = soft_union_probability_points(area_points, st.active, sigma)
```

解释：点属于 activation 区域的 soft 概率。

**L0272**

```python
        p_protected = soft_union_probability_points(area_points, st.erk, sigma)
```

解释：点属于 ERK 保护区域的 soft 概率。

**L0273**

```python
        return AREA_W * float(np.mean(p_active * (1.0 - p_protected)))
```

解释：返回结果给调用这个函数的地方。

**L0274**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0275**

```python
    raise ValueError(f"Unknown likelihood mode: {mode}")
```

解释：主动抛出 ValueError，说明输入或配置不合法。

**L0276**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0277**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0278**

```python
def death_event_intensity(
```

解释：定义函数：计算观测死亡点在死亡前瞬间的条件强度。

**L0279**

```python
    x: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0280**

```python
    y: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0281**

```python
    st: ParticleState,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0282**

```python
    p: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0283**

```python
    mode: str = "exact",
```

解释：ParticleState 的字段 mode，保存粒子状态的一部分。

**L0284**

```python
    sigma: float = SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0285**

```python
    min_intensity: float = MIN_EVENT_INTENSITY,
```

解释：ParticleState 的字段 min_intensity，保存粒子状态的一部分。

**L0286**

```python
) -> float:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0287**

```python
    """lambda^d_theta(y,s | Z_{s-}) before the observed death triggers ERK."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0288**

```python
    if mode == "exact":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0289**

```python
        ok = inside_union_exact(x, y, st.active) and (not inside_union_exact(x, y, st.erk))
```

解释：布尔变量：这个死亡点是否处在 active 且 unprotected 区域。

**L0290**

```python
        return p.lambda_d if ok else min_intensity
```

解释：返回结果给调用这个函数的地方。

**L0291**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0292**

```python
    if mode == "soft":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0293**

```python
        pa = soft_union_probability_one(x, y, st.active, sigma)
```

解释：activation 事件在总率中的概率。

**L0294**

```python
        pp = soft_union_probability_one(x, y, st.erk, sigma)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0295**

```python
        return max(min_intensity, p.lambda_d * pa * (1.0 - pp))
```

解释：返回结果给调用这个函数的地方。

**L0296**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0297**

```python
    raise ValueError(f"Unknown likelihood mode: {mode}")
```

解释：主动抛出 ValueError，说明输入或配置不合法。

**L0298**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0299**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0300**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。


### 第 301–350 行

**L0301**

```python
# 4. Synthetic simulator: exact Gillespie model, no plots
```

解释：合成数据模拟器：用 exact Gillespie 模型生成死亡事件。

**L0302**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0303**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0304**

```python
def simulate_death_events(
```

解释：定义函数：用原始 exact Gillespie 模型模拟合成死亡数据。

**L0305**

```python
    p: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0306**

```python
    T_max: float = T_MAX,
```

解释：ParticleState 的字段 T_max，保存粒子状态的一部分。

**L0307**

```python
    target_deaths: int | None = TARGET_DEATHS,
```

解释：ParticleState 的字段 target_deaths，保存粒子状态的一部分。

**L0308**

```python
    seed: int = 123,
```

解释：ParticleState 的字段 seed，保存粒子状态的一部分。

**L0309**

```python
) -> Dict[str, np.ndarray]:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0310**

```python
    """Simulate the original model and return death events plus hidden histories."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0311**

```python
    if not valid_params(p):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0312**

```python
        raise ValueError("Invalid parameters for simulation.")
```

解释：主动抛出 ValueError，说明输入或配置不合法。

**L0313**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0314**

```python
    rng = np.random.default_rng(seed)
```

解释：NumPy 随机数生成器。

**L0315**

```python
    st = ParticleState(active=[], erk=[])
```

解释：当前粒子的状态。

**L0316**

```python
    t = 0.0
```

解释：当前模拟时间。

**L0317**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0318**

```python
    cas_events: List[Tuple[float, float, float]] = []
```

解释：隐藏 caspase activation 历史。

**L0319**

```python
    death_events: List[Tuple[float, float, float]] = []
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0320**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0321**

```python
    while t < T_max and (target_deaths is None or len(death_events) < target_deaths):
```

解释：while 循环：只要条件成立，就反复执行下面缩进代码。

**L0322**

```python
        n_active = len(st.active)
```

解释：当前 active 圆盘数量。

**L0323**

```python
        n_erk = len(st.erk)
```

解释：当前 ERK 圆盘数量。

**L0324**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0325**

```python
        activation_proposal_rate = p.lambda_a_1 * AREA_W
```

解释：activation 候选事件的 proposal 总强度。

**L0326**

```python
        death_proposal_rate = p.lambda_d * AREA_W
```

解释：death 候选事件的 proposal 总强度。

**L0327**

```python
        active_expiration_rate = n_active * p.beta_a_T
```

解释：active 圆盘过期事件总强度。

**L0328**

```python
        erk_expiration_rate = n_erk * p.beta_d_T
```

解释：ERK 圆盘过期事件总强度。

**L0329**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0330**

```python
        a0 = activation_proposal_rate + death_proposal_rate + active_expiration_rate + erk_expiration_rate
```

解释：Gillespie 总事件率。

**L0331**

```python
        if a0 <= 0.0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0332**

```python
            break
```

解释：跳出当前循环。

**L0333**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0334**

```python
        t += rng.exponential(1.0 / a0)
```

解释：从指数分布中抽等待时间或半径；Gillespie 中等待时间常用指数分布。

**L0335**

```python
        if t > T_max:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0336**

```python
            break
```

解释：跳出当前循环。

**L0337**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0338**

```python
        u = rng.uniform()
```

解释：一个 U(0,1) 随机数，用于决定发生哪类事件。

**L0339**

```python
        pa = activation_proposal_rate / a0
```

解释：activation 事件在总率中的概率。

**L0340**

```python
        pd = death_proposal_rate / a0
```

解释：death 事件在总率中的概率。

**L0341**

```python
        pe = active_expiration_rate / a0
```

解释：active expiration 事件在总率中的概率。

**L0342**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0343**

```python
        if u <= pa:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0344**

```python
            # Candidate activation, thinned by local activation intensity.
```

解释：注释：Candidate activation, thinned by local activation intensity.。

**L0345**

```python
            x = rng.uniform(0.0, Lx)
```

解释：随机事件位置的 x 坐标。

**L0346**

```python
            y = rng.uniform(0.0, Ly)
```

解释：随机事件位置的 y 坐标。

**L0347**

```python
            lam = local_activation_intensity(x, y, st, p)
```

解释：当前位置的 activation intensity。

**L0348**

```python
            if rng.uniform() <= lam / p.lambda_a_1:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0349**

```python
                r = rng.exponential(1.0 / p.beta_a_R)
```

解释：activation 圆盘半径。

**L0350**

```python
                st.active.append((x, y, r))
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。


### 第 351–400 行

**L0351**

```python
                cas_events.append((x, y, t))
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。

**L0352**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0353**

```python
        elif u <= pa + pd:
```

解释：否则如果：前面的 if/elif 不成立时，再检查这个条件。

**L0354**

```python
            # Candidate death, accepted iff active and unprotected.
```

解释：注释：Candidate death, accepted iff active and unprotected.。

**L0355**

```python
            x = rng.uniform(0.0, Lx)
```

解释：随机事件位置的 x 坐标。

**L0356**

```python
            y = rng.uniform(0.0, Ly)
```

解释：随机事件位置的 y 坐标。

**L0357**

```python
            if inside_union_exact(x, y, st.active) and (not inside_union_exact(x, y, st.erk)):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0358**

```python
                death_events.append((x, y, t))
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。

**L0359**

```python
                rE = rng.exponential(1.0 / p.beta_d_R)
```

解释：ERK 保护圆盘半径。

**L0360**

```python
                st.erk.append((x, y, rE))
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。

**L0361**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0362**

```python
        elif u <= pa + pd + pe:
```

解释：否则如果：前面的 if/elif 不成立时，再检查这个条件。

**L0363**

```python
            # Active expiration.
```

解释：注释：Active expiration.。

**L0364**

```python
            if st.active:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0365**

```python
                idx = rng.integers(0, len(st.active))
```

解释：随机选择要删除/过期的圆盘下标。

**L0366**

```python
                st.active.pop(int(idx))
```

解释：从列表中删除一个元素；这里表示某个 active/ERK 圆盘过期。

**L0367**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0368**

```python
        else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0369**

```python
            # ERK expiration.
```

解释：注释：ERK expiration.。

**L0370**

```python
            if st.erk:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0371**

```python
                idx = rng.integers(0, len(st.erk))
```

解释：随机选择要删除/过期的圆盘下标。

**L0372**

```python
                st.erk.pop(int(idx))
```

解释：从列表中删除一个元素；这里表示某个 active/ERK 圆盘过期。

**L0373**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0374**

```python
    return {
```

解释：返回结果给调用这个函数的地方。

**L0375**

```python
        "death_events": np.array(death_events, dtype=float),  # columns: x,y,t
```

解释：ParticleState 的字段 "death_events"，保存粒子状态的一部分。

**L0376**

```python
        "cas_events": np.array(cas_events, dtype=float),
```

解释：ParticleState 的字段 "cas_events"，保存粒子状态的一部分。

**L0377**

```python
        "final_time": np.array([t], dtype=float),
```

解释：ParticleState 的字段 "final_time"，保存粒子状态的一部分。

**L0378**

```python
    }
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0379**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0380**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0381**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0382**

```python
# 5. Particle filter likelihood conditional on observed deaths
```

解释：粒子滤波似然：在观测死亡条件下传播隐藏状态。

**L0383**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0384**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0385**

```python
def propagate_hidden_until(
```

解释：定义函数：在两个观测死亡时间之间传播隐藏过程，并累计无死亡生存项。

**L0386**

```python
    st: ParticleState,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0387**

```python
    t0: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0388**

```python
    t1: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0389**

```python
    p: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0390**

```python
    rng: np.random.Generator,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0391**

```python
    area_points: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0392**

```python
    mode: str,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0393**

```python
    sigma: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0394**

```python
) -> float:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0395**

```python
    """
```

解释：三引号：开始或结束一段多行说明文字/文档字符串，Python 会把它当作字符串。

**L0396**

```python
    Propagate only the hidden mechanisms between observed death times:
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0397**

```python
      - activation proposals/accepted activations;
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0398**

```python
      - active expirations;
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0399**

```python
      - ERK expirations.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0400**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。


### 第 401–450 行

**L0401**

```python
    Deaths are not simulated here because they are observed. Their likelihood
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0402**

```python
    contribution is accumulated as exp(-integral lambda) between events and
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0403**

```python
    lambda(y,s | Z_{s-}) at each observed death.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0404**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0405**

```python
    Returns log survival factor: -int_{t0}^{t1} lambda_d |A(Va)\\A(Vp)| dt.
```

解释：文档字符串内容：给读代码的人看的说明，不直接执行算法。

**L0406**

```python
    """
```

解释：三引号：开始或结束一段多行说明文字/文档字符串，Python 会把它当作字符串。

**L0407**

```python
    t = t0
```

解释：当前模拟时间。

**L0408**

```python
    log_survival = 0.0
```

解释：无死亡区间的 log 生存因子，即 -∫ hazard dt。

**L0409**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0410**

```python
    while t < t1:
```

解释：while 循环：只要条件成立，就反复执行下面缩进代码。

**L0411**

```python
        n_active = len(st.active)
```

解释：当前 active 圆盘数量。

**L0412**

```python
        n_erk = len(st.erk)
```

解释：当前 ERK 圆盘数量。

**L0413**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0414**

```python
        activation_proposal_rate = p.lambda_a_1 * AREA_W
```

解释：activation 候选事件的 proposal 总强度。

**L0415**

```python
        active_expiration_rate = n_active * p.beta_a_T
```

解释：active 圆盘过期事件总强度。

**L0416**

```python
        erk_expiration_rate = n_erk * p.beta_d_T
```

解释：ERK 圆盘过期事件总强度。

**L0417**

```python
        a0_hidden = activation_proposal_rate + active_expiration_rate + erk_expiration_rate
```

解释：隐藏机制总事件率，不包括观测死亡事件。

**L0418**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0419**

```python
        # Current observed-death hazard under this particle.
```

解释：注释：Current observed-death hazard under this particle.。

**L0420**

```python
        death_area = active_unprotected_area(st, area_points, mode=mode, sigma=sigma)
```

解释：当前粒子 active 且不被 ERK 保护的面积近似。

**L0421**

```python
        death_hazard = p.lambda_d * death_area
```

解释：当前粒子的死亡总 hazard = lambda_d × 面积。

**L0422**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0423**

```python
        if a0_hidden <= 0.0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0424**

```python
            log_survival -= death_hazard * (t1 - t)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0425**

```python
            break
```

解释：跳出当前循环。

**L0426**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0427**

```python
        dt = rng.exponential(1.0 / a0_hidden)
```

解释：下一次隐藏事件前的等待时间。

**L0428**

```python
        if t + dt >= t1:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0429**

```python
            log_survival -= death_hazard * (t1 - t)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0430**

```python
            t = t1
```

解释：当前模拟时间。

**L0431**

```python
            break
```

解释：跳出当前循环。

**L0432**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0433**

```python
        log_survival -= death_hazard * dt
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0434**

```python
        t += dt
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0435**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0436**

```python
        u = rng.uniform()
```

解释：一个 U(0,1) 随机数，用于决定发生哪类事件。

**L0437**

```python
        pa = activation_proposal_rate / a0_hidden
```

解释：activation 事件在总率中的概率。

**L0438**

```python
        pe = active_expiration_rate / a0_hidden
```

解释：active expiration 事件在总率中的概率。

**L0439**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0440**

```python
        if u <= pa:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0441**

```python
            x = rng.uniform(0.0, Lx)
```

解释：随机事件位置的 x 坐标。

**L0442**

```python
            y = rng.uniform(0.0, Ly)
```

解释：随机事件位置的 y 坐标。

**L0443**

```python
            lam = local_activation_intensity(x, y, st, p)
```

解释：当前位置的 activation intensity。

**L0444**

```python
            if rng.uniform() <= lam / p.lambda_a_1:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0445**

```python
                r = rng.exponential(1.0 / p.beta_a_R)
```

解释：activation 圆盘半径。

**L0446**

```python
                st.active.append((x, y, r))
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。

**L0447**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0448**

```python
        elif u <= pa + pe:
```

解释：否则如果：前面的 if/elif 不成立时，再检查这个条件。

**L0449**

```python
            if st.active:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0450**

```python
                idx = rng.integers(0, len(st.active))
```

解释：随机选择要删除/过期的圆盘下标。


### 第 451–500 行

**L0451**

```python
                st.active.pop(int(idx))
```

解释：从列表中删除一个元素；这里表示某个 active/ERK 圆盘过期。

**L0452**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0453**

```python
        else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0454**

```python
            if st.erk:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0455**

```python
                idx = rng.integers(0, len(st.erk))
```

解释：随机选择要删除/过期的圆盘下标。

**L0456**

```python
                st.erk.pop(int(idx))
```

解释：从列表中删除一个元素；这里表示某个 active/ERK 圆盘过期。

**L0457**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0458**

```python
    return log_survival
```

解释：返回结果给调用这个函数的地方。

**L0459**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0460**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0461**

```python
def logsumexp_np(a: np.ndarray) -> float:
```

解释：定义函数：稳定计算 log(sum(exp(a)))，避免指数上溢/下溢。

**L0462**

```python
    m = float(np.max(a))
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0463**

```python
    if not np.isfinite(m):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0464**

```python
        return -np.inf
```

解释：返回结果给调用这个函数的地方。

**L0465**

```python
    return m + math.log(float(np.sum(np.exp(a - m))))
```

解释：返回结果给调用这个函数的地方。

**L0466**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0467**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0468**

```python
def _normalize_weights_safe(weights: np.ndarray) -> np.ndarray:
```

解释：定义函数：把非负权重归一化，并检查是否可归一化。

**L0469**

```python
    """Numerically safe normalization for already nonnegative weights."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0470**

```python
    weights = np.asarray(weights, dtype=float)
```

解释：普通尺度的粒子权重。

**L0471**

```python
    total = float(np.sum(weights))
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0472**

```python
    if (not np.isfinite(total)) or total <= 0.0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0473**

```python
        raise ValueError("Cannot resample: weights are not normalizable.")
```

解释：主动抛出 ValueError，说明输入或配置不合法。

**L0474**

```python
    weights = weights / total
```

解释：普通尺度的粒子权重。

**L0475**

```python
    # Make the last cumulative value exactly 1.0 after cumsum.
```

解释：注释：Make the last cumulative value exactly 1.0 after cumsum.。

**L0476**

```python
    weights[-1] = max(0.0, 1.0 - float(np.sum(weights[:-1])))
```

解释：ParticleState 的字段 weights[-1]，保存粒子状态的一部分。

**L0477**

```python
    return weights
```

解释：返回结果给调用这个函数的地方。

**L0478**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0479**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0480**

```python
def multinomial_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
```

解释：定义函数：多项式重采样：按权重独立抽 N 次祖先。

**L0481**

```python
    """Basic multinomial redistribution: N iid draws from the discrete weights."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0482**

```python
    weights = _normalize_weights_safe(weights)
```

解释：普通尺度的粒子权重。

**L0483**

```python
    n = len(weights)
```

解释：数量变量，通常表示点数或粒子数。

**L0484**

```python
    return rng.choice(n, size=n, replace=True, p=weights)
```

解释：返回结果给调用这个函数的地方。

**L0485**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0486**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0487**

```python
def systematic_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
```

解释：定义函数：系统重采样：用等距点减少随机性。

**L0488**

```python
    """Kitagawa/systematic redistribution: u_1~U(0,1/N), u_i=u_1+(i-1)/N."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0489**

```python
    weights = _normalize_weights_safe(weights)
```

解释：普通尺度的粒子权重。

**L0490**

```python
    n = len(weights)
```

解释：数量变量，通常表示点数或粒子数。

**L0491**

```python
    positions = (rng.uniform() + np.arange(n)) / n
```

解释：从均匀分布中抽随机数；用于随机位置或随机选择事件类型。

**L0492**

```python
    cumsum = np.cumsum(weights)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0493**

```python
    cumsum[-1] = 1.0
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0494**

```python
    return np.searchsorted(cumsum, positions, side="right")
```

解释：返回结果给调用这个函数的地方。

**L0495**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0496**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0497**

```python
def stratified_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
```

解释：定义函数：分层重采样：每个小区间抽一个点。

**L0498**

```python
    """Stratified redistribution: one uniform draw in each interval [i/N,(i+1)/N)."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0499**

```python
    weights = _normalize_weights_safe(weights)
```

解释：普通尺度的粒子权重。

**L0500**

```python
    n = len(weights)
```

解释：数量变量，通常表示点数或粒子数。


### 第 501–550 行

**L0501**

```python
    positions = (np.arange(n) + rng.uniform(size=n)) / n
```

解释：从均匀分布中抽随机数；用于随机位置或随机选择事件类型。

**L0502**

```python
    cumsum = np.cumsum(weights)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0503**

```python
    cumsum[-1] = 1.0
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0504**

```python
    return np.searchsorted(cumsum, positions, side="right")
```

解释：返回结果给调用这个函数的地方。

**L0505**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0506**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0507**

```python
def residual_multinomial_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
```

解释：定义函数：残差+多项式重采样：先确定性复制 floor(Nw_i)，剩余部分多项式抽。

**L0508**

```python
    """Residual redistribution: deterministic floor(Nw_i) copies, multinomial for residues."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0509**

```python
    weights = _normalize_weights_safe(weights)
```

解释：普通尺度的粒子权重。

**L0510**

```python
    n = len(weights)
```

解释：数量变量，通常表示点数或粒子数。

**L0511**

```python
    counts = np.floor(n * weights).astype(int)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0512**

```python
    ancestors = [i for i, c in enumerate(counts) for _ in range(int(c))]
```

解释：重采样选出的祖先粒子编号。

**L0513**

```python
    r = n - len(ancestors)
```

解释：activation 圆盘半径。

**L0514**

```python
    if r > 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0515**

```python
        residual = n * weights - counts
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0516**

```python
        residual_sum = float(np.sum(residual))
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0517**

```python
        if residual_sum <= 0.0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0518**

```python
            extra = rng.integers(0, n, size=r)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0519**

```python
        else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0520**

```python
            residual = residual / residual_sum
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0521**

```python
            residual[-1] = max(0.0, 1.0 - float(np.sum(residual[:-1])))
```

解释：ParticleState 的字段 residual[-1]，保存粒子状态的一部分。

**L0522**

```python
            extra = rng.choice(n, size=r, replace=True, p=residual)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0523**

```python
        ancestors.extend(map(int, extra))
```

解释：把多个元素追加到列表末尾。

**L0524**

```python
    ancestors = np.asarray(ancestors, dtype=int)
```

解释：重采样选出的祖先粒子编号。

**L0525**

```python
    rng.shuffle(ancestors)
```

解释：随机打乱数组顺序，避免重采样结果有固定排列。

**L0526**

```python
    return ancestors
```

解释：返回结果给调用这个函数的地方。

**L0527**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0528**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0529**

```python
def residual_systematic_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
```

解释：定义函数：残差+系统重采样：先确定性复制，再对残差系统抽样。

**L0530**

```python
    """Residual + Kitagawa: deterministic floor(Nw_i) copies, systematic for residues."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0531**

```python
    weights = _normalize_weights_safe(weights)
```

解释：普通尺度的粒子权重。

**L0532**

```python
    n = len(weights)
```

解释：数量变量，通常表示点数或粒子数。

**L0533**

```python
    counts = np.floor(n * weights).astype(int)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0534**

```python
    ancestors = [i for i, c in enumerate(counts) for _ in range(int(c))]
```

解释：重采样选出的祖先粒子编号。

**L0535**

```python
    r = n - len(ancestors)
```

解释：activation 圆盘半径。

**L0536**

```python
    if r > 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0537**

```python
        residual = n * weights - counts
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0538**

```python
        residual_sum = float(np.sum(residual))
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0539**

```python
        if residual_sum <= 0.0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0540**

```python
            extra = rng.integers(0, n, size=r)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0541**

```python
        else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0542**

```python
            residual = residual / residual_sum
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0543**

```python
            residual[-1] = max(0.0, 1.0 - float(np.sum(residual[:-1])))
```

解释：ParticleState 的字段 residual[-1]，保存粒子状态的一部分。

**L0544**

```python
            positions = (rng.uniform() + np.arange(r)) / r
```

解释：从均匀分布中抽随机数；用于随机位置或随机选择事件类型。

**L0545**

```python
            cumsum = np.cumsum(residual)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0546**

```python
            cumsum[-1] = 1.0
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0547**

```python
            extra = np.searchsorted(cumsum, positions, side="right")
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0548**

```python
        ancestors.extend(map(int, extra))
```

解释：把多个元素追加到列表末尾。

**L0549**

```python
    ancestors = np.asarray(ancestors, dtype=int)
```

解释：重采样选出的祖先粒子编号。

**L0550**

```python
    rng.shuffle(ancestors)
```

解释：随机打乱数组顺序，避免重采样结果有固定排列。


### 第 551–600 行

**L0551**

```python
    return ancestors
```

解释：返回结果给调用这个函数的地方。

**L0552**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0553**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0554**

```python
def resample_indices(weights: np.ndarray, rng: np.random.Generator, method: str = RESAMPLE_METHOD) -> np.ndarray:
```

解释：定义函数：根据字符串选择具体重采样方法。

**L0555**

```python
    """Choose the redistribution scheme used by the particle filter."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0556**

```python
    if method == "multinomial":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0557**

```python
        return multinomial_resample(weights, rng)
```

解释：返回结果给调用这个函数的地方。

**L0558**

```python
    if method == "systematic":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0559**

```python
        return systematic_resample(weights, rng)
```

解释：返回结果给调用这个函数的地方。

**L0560**

```python
    if method == "stratified":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0561**

```python
        return stratified_resample(weights, rng)
```

解释：返回结果给调用这个函数的地方。

**L0562**

```python
    if method == "residual_multinomial":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0563**

```python
        return residual_multinomial_resample(weights, rng)
```

解释：返回结果给调用这个函数的地方。

**L0564**

```python
    if method == "residual_systematic":
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0565**

```python
        return residual_systematic_resample(weights, rng)
```

解释：返回结果给调用这个函数的地方。

**L0566**

```python
    raise ValueError(f"Unknown RESAMPLE_METHOD={method!r}")
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0567**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0568**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0569**

```python
def particle_loglikelihood(
```

解释：定义函数：用 bootstrap particle filter 估计观测死亡事件的 log-likelihood。

**L0570**

```python
    death_events: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0571**

```python
    p: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0572**

```python
    T_end: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0573**

```python
    n_particles: int = N_PARTICLES,
```

解释：ParticleState 的字段 n_particles，保存粒子状态的一部分。

**L0574**

```python
    area_points: np.ndarray | None = None,
```

解释：ParticleState 的字段 area_points，保存粒子状态的一部分。

**L0575**

```python
    seed: int = PF_SEED,
```

解释：ParticleState 的字段 seed，保存粒子状态的一部分。

**L0576**

```python
    resample_threshold: float = RESAMPLE_THRESHOLD,
```

解释：ParticleState 的字段 resample_threshold，保存粒子状态的一部分。

**L0577**

```python
    resample_method: str = RESAMPLE_METHOD,
```

解释：ParticleState 的字段 resample_method，保存粒子状态的一部分。

**L0578**

```python
    mode: str = LIKELIHOOD_MODE,
```

解释：ParticleState 的字段 mode，保存粒子状态的一部分。

**L0579**

```python
    sigma: float = SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0580**

```python
    verbose: bool = False,
```

解释：ParticleState 的字段 verbose，保存粒子状态的一部分。

**L0581**

```python
) -> float:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0582**

```python
    """Bootstrap particle estimate of log p_theta(Y^d_{0:T})."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0583**

```python
    if not valid_params(p):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0584**

```python
        return -np.inf
```

解释：返回结果给调用这个函数的地方。

**L0585**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0586**

```python
    if area_points is None:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0587**

```python
        rng_area = np.random.default_rng(AREA_SEED)
```

解释：创建 NumPy 随机数生成器；给定 seed 可让结果可重复。

**L0588**

```python
        area_points = np.column_stack([
```

解释：把若干一维数组按列拼成二维数组；这里通常用于生成 (x,y) 点。

**L0589**

```python
            rng_area.uniform(0.0, Lx, AREA_MC_POINTS),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0590**

```python
            rng_area.uniform(0.0, Ly, AREA_MC_POINTS),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0591**

```python
        ])
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0592**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0593**

```python
    if death_events.size == 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0594**

```python
        death_events = np.empty((0, 3), dtype=float)
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0595**

```python
    else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0596**

```python
        death_events = np.asarray(death_events, dtype=float)
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0597**

```python
        order = np.argsort(death_events[:, 2])
```

解释：ParticleState 的字段 order，保存粒子状态的一部分。

**L0598**

```python
        death_events = death_events[order]
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0599**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0600**

```python
    rng = np.random.default_rng(seed)
```

解释：NumPy 随机数生成器。


### 第 601–650 行

**L0601**

```python
    states = [ParticleState(active=[], erk=[]) for _ in range(n_particles)]
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0602**

```python
    logw = np.full(n_particles, -math.log(n_particles), dtype=float)
```

解释：粒子的 log 权重。

**L0603**

```python
    loglik = 0.0
```

解释：累计的 log-likelihood 估计。

**L0604**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0605**

```python
    t_prev = 0.0
```

解释：上一个观测死亡时间。

**L0606**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0607**

```python
    # Process observed deaths in chronological order.
```

解释：注释：Process observed deaths in chronological order.。

**L0608**

```python
    for k, (x_d, y_d, s_d) in enumerate(death_events, start=1):
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0609**

```python
        if s_d < t_prev:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0610**

```python
            raise ValueError("Death events must be sorted by increasing time.")
```

解释：主动抛出 ValueError，说明输入或配置不合法。

**L0611**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0612**

```python
        logG = np.empty(n_particles, dtype=float)
```

解释：本个观测区间对每个粒子的 log 增量权重。

**L0613**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0614**

```python
        for i, st in enumerate(states):
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0615**

```python
            val = propagate_hidden_until(st, t_prev, float(s_d), p, rng, area_points, mode, sigma)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0616**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0617**

```python
            # Use pre-jump state Z_{s-} for the likelihood contribution.
```

解释：注释：Use pre-jump state Z_{s-} for the 似然 contribution.。

**L0618**

```python
            lam_event = death_event_intensity(float(x_d), float(y_d), st, p, mode=mode, sigma=sigma)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0619**

```python
            val += math.log(lam_event)
```

解释：计算对数；用 log-space 可以让正参数优化和权重计算更稳定。

**L0620**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0621**

```python
            # After observing the death, update common death history implicitly,
```

解释：注释：After observing the death, update common death history implicitly,。

**L0622**

```python
            # and sample the hidden ERK protection mark for this particle.
```

解释：注释：and sample the hidden ERK protection mark for this particle.。

**L0623**

```python
            rE = rng.exponential(1.0 / p.beta_d_R)
```

解释：ERK 保护圆盘半径。

**L0624**

```python
            st.erk.append((float(x_d), float(y_d), rE))
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。

**L0625**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0626**

```python
            logG[i] = val
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0627**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0628**

```python
        new_logw_unnorm = logw + logG
```

解释：还没归一化的新 log 权重。

**L0629**

```python
        inc = logsumexp_np(new_logw_unnorm)
```

解释：本次观测带来的 log 归一化常数，也是 log-likelihood 增量。

**L0630**

```python
        if not np.isfinite(inc):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0631**

```python
            if verbose:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0632**

```python
                print(f"All particles collapsed at observed death {k}.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0633**

```python
            return -np.inf
```

解释：返回结果给调用这个函数的地方。

**L0634**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0635**

```python
        loglik += inc
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0636**

```python
        logw = new_logw_unnorm - inc
```

解释：粒子的 log 权重。

**L0637**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0638**

```python
        weights = np.exp(logw)
```

解释：普通尺度的粒子权重。

**L0639**

```python
        neff = 1.0 / float(np.sum(weights ** 2))
```

解释：有效样本量 ESS。

**L0640**

```python
        if neff / n_particles <= resample_threshold:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0641**

```python
            ancestors = resample_indices(weights, rng, method=resample_method)
```

解释：重采样选出的祖先粒子编号。

**L0642**

```python
            states = [clone_state(states[int(j)]) for j in ancestors]
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0643**

```python
            logw.fill(-math.log(n_particles))
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0644**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0645**

```python
        t_prev = float(s_d)
```

解释：上一个观测死亡时间。

**L0646**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0647**

```python
    # Final no-death interval [last death, T_end].
```

解释：注释：Final no-death interval [last death, T_end].。

**L0648**

```python
    if T_end > t_prev:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0649**

```python
        logG = np.empty(n_particles, dtype=float)
```

解释：本个观测区间对每个粒子的 log 增量权重。

**L0650**

```python
        for i, st in enumerate(states):
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。


### 第 651–700 行

**L0651**

```python
            logG[i] = propagate_hidden_until(st, t_prev, T_end, p, rng, area_points, mode, sigma)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0652**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0653**

```python
        new_logw_unnorm = logw + logG
```

解释：还没归一化的新 log 权重。

**L0654**

```python
        inc = logsumexp_np(new_logw_unnorm)
```

解释：本次观测带来的 log 归一化常数，也是 log-likelihood 增量。

**L0655**

```python
        if not np.isfinite(inc):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0656**

```python
            return -np.inf
```

解释：返回结果给调用这个函数的地方。

**L0657**

```python
        loglik += inc
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0658**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0659**

```python
    return float(loglik)
```

解释：返回结果给调用这个函数的地方。

**L0660**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0661**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0662**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0663**

```python
# 6. Parameter fitting by particle maximum likelihood
```

解释：参数估计：用优化器最大化粒子滤波似然。

**L0664**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0665**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0666**

```python
def fit_parameters(
```

解释：定义函数：外层参数估计：最大化粒子滤波似然。

**L0667**

```python
    death_events: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0668**

```python
    base_params: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0669**

```python
    keys: Sequence[str],
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0670**

```python
    T_end: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0671**

```python
    n_particles: int = N_PARTICLES,
```

解释：ParticleState 的字段 n_particles，保存粒子状态的一部分。

**L0672**

```python
    area_mc_points: int = AREA_MC_POINTS,
```

解释：ParticleState 的字段 area_mc_points，保存粒子状态的一部分。

**L0673**

```python
    pf_seed: int = PF_SEED,
```

解释：ParticleState 的字段 pf_seed，保存粒子状态的一部分。

**L0674**

```python
    pf_replicates: int = PF_REPLICATES,
```

解释：ParticleState 的字段 pf_replicates，保存粒子状态的一部分。

**L0675**

```python
    resample_method: str = RESAMPLE_METHOD,
```

解释：ParticleState 的字段 resample_method，保存粒子状态的一部分。

**L0676**

```python
    mode: str = LIKELIHOOD_MODE,
```

解释：ParticleState 的字段 mode，保存粒子状态的一部分。

**L0677**

```python
    sigma: float = SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0678**

```python
    maxiter: int = OPT_MAXITER,
```

解释：ParticleState 的字段 maxiter，保存粒子状态的一部分。

**L0679**

```python
    popsize: int = OPT_POPSIZE,
```

解释：ParticleState 的字段 popsize，保存粒子状态的一部分。

**L0680**

```python
    polish: bool = POLISH_WITH_LBFGSB,
```

解释：ParticleState 的字段 polish，保存粒子状态的一部分。

**L0681**

```python
) -> Tuple[ModelParams, float]:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0682**

```python
    """Maximize the particle likelihood over selected log-parameters."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0683**

```python
    rng_area = np.random.default_rng(AREA_SEED)
```

解释：创建 NumPy 随机数生成器；给定 seed 可让结果可重复。

**L0684**

```python
    area_points = np.column_stack([
```

解释：把若干一维数组按列拼成二维数组；这里通常用于生成 (x,y) 点。

**L0685**

```python
        rng_area.uniform(0.0, Lx, area_mc_points),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0686**

```python
        rng_area.uniform(0.0, Ly, area_mc_points),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0687**

```python
    ])
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0688**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0689**

```python
    bounds = log_bounds(keys)
```

解释：优化变量的 log-space 边界。

**L0690**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0691**

```python
    eval_counter = {"n": 0, "best": np.inf}
```

解释：记录优化过程中函数评估次数和当前最好目标值。

**L0692**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0693**

```python
    def objective(log_vec: np.ndarray) -> float:
```

解释：定义函数：给优化器调用的目标函数：返回负的平均 log-likelihood。

**L0694**

```python
        t_start = time.time()
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0695**

```python
        eval_counter["n"] += 1
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0696**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0697**

```python
        p = unpack_log_params(log_vec, base_params, keys)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0698**

```python
        if not valid_params(p):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0699**

```python
            return 1e100
```

解释：返回结果给调用这个函数的地方。

**L0700**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。


### 第 701–750 行

**L0701**

```python
        total = 0.0
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0702**

```python
        for r in range(pf_replicates):
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0703**

```python
            ll = particle_loglikelihood(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0704**

```python
                death_events=death_events,
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0705**

```python
                p=p,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0706**

```python
                T_end=T_end,
```

解释：观测窗口终点。

**L0707**

```python
                n_particles=n_particles,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0708**

```python
                area_points=area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0709**

```python
                seed=pf_seed + 1009 * r,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0710**

```python
                resample_method=resample_method,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0711**

```python
                mode=mode,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0712**

```python
                sigma=sigma,
```

解释：soft indicator 的平滑尺度。

**L0713**

```python
                verbose=False,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0714**

```python
            )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0715**

```python
            if not np.isfinite(ll):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0716**

```python
                return 1e90
```

解释：返回结果给调用这个函数的地方。

**L0717**

```python
            total += ll
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0718**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0719**

```python
        obj = -total / pf_replicates
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0720**

```python
        if obj < eval_counter["best"]:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0721**

```python
            eval_counter["best"] = float(obj)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0722**

```python
            best_mark = "  NEW BEST"
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0723**

```python
        else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0724**

```python
            best_mark = ""
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0725**

```python
        elapsed = time.time() - t_start
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0726**

```python
        vals = ", ".join(f"{k}={getattr(p, k):.5g}" for k in keys)
```

解释：把参数值收集成列表，方便统一检查。

**L0727**

```python
        print(
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0728**

```python
            f"eval {eval_counter['n']:04d}: obj={obj:.4f}, loglik={-obj:.4f}, "
```

解释：ParticleState 的字段 f"eval {eval_counter['n']，保存粒子状态的一部分。

**L0729**

```python
            f"time={elapsed:.2f}s, {vals}{best_mark}",
```

解释：ParticleState 的字段 f"time，保存粒子状态的一部分。

**L0730**

```python
            flush=True,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0731**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0732**

```python
        return obj
```

解释：返回结果给调用这个函数的地方。

**L0733**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0734**

```python
    print("\nStarting differential evolution optimization...")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0735**

```python
    print(f"  estimating keys: {list(keys)}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0736**

```python
    print(f"  mode={mode}, particles={n_particles}, area points={area_mc_points}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0737**

```python
    print(f"  resampling={resample_method}, threshold={RESAMPLE_THRESHOLD}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0738**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0739**

```python
    result_de = differential_evolution(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0740**

```python
        objective,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0741**

```python
        bounds=bounds,
```

解释：优化变量的 log-space 边界。

**L0742**

```python
        maxiter=maxiter,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0743**

```python
        popsize=popsize,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0744**

```python
        polish=False,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0745**

```python
        seed=987654,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0746**

```python
        updating="immediate",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0747**

```python
        workers=1,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0748**

```python
        disp=True,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0749**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0750**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。


### 第 751–800 行

**L0751**

```python
    best_x = result_de.x
```

解释：当前最优的 log 参数向量。

**L0752**

```python
    best_obj = float(result_de.fun)
```

解释：当前最优目标函数值。

**L0753**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0754**

```python
    if polish:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0755**

```python
        print("\nPolishing with L-BFGS-B...")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0756**

```python
        result_local = minimize(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0757**

```python
            objective,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0758**

```python
            best_x,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0759**

```python
            method="L-BFGS-B",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0760**

```python
            bounds=bounds,
```

解释：优化变量的 log-space 边界。

**L0761**

```python
            options={"maxiter": 30, "ftol": 1e-3},
```

解释：ParticleState 的字段 options，保存粒子状态的一部分。

**L0762**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0763**

```python
        if result_local.fun < best_obj:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0764**

```python
            best_x = result_local.x
```

解释：当前最优的 log 参数向量。

**L0765**

```python
            best_obj = float(result_local.fun)
```

解释：当前最优目标函数值。

**L0766**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0767**

```python
    best_params = unpack_log_params(best_x, base_params, keys)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0768**

```python
    return best_params, -best_obj
```

解释：返回结果给调用这个函数的地方。

**L0769**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0770**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0771**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0772**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0773**

```python
# 7. Diagnostics
```

解释：诊断函数：检查空间信号、PF 噪声和似然剖面。

**L0774**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0775**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0776**

```python
def death_spatial_diagnostic(deaths: np.ndarray) -> None:
```

解释：定义函数：打印死亡点在 T-zone 内外的数量、密度、密度比。

**L0777**

```python
    """Print whether deaths are enriched inside the fixed T-zone."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0778**

```python
    if deaths.size == 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0779**

```python
        print("\nDeath spatial diagnostic: no deaths.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0780**

```python
        return
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0781**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0782**

```python
    n_total = len(deaths)
```

解释：死亡事件总数。

**L0783**

```python
    n_T = int(sum(is_inside_T_zone(float(x), float(y)) for x, y, _ in deaths))
```

解释：落在 T-zone 里的死亡数。

**L0784**

```python
    n_out = n_total - n_T
```

解释：落在 T-zone 外的死亡数。

**L0785**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0786**

```python
    area_T = (x2 - x1) * Ly + x1 * (y2 - y1)
```

解释：T-zone 面积。

**L0787**

```python
    area_out = AREA_W - area_T
```

解释：T-zone 外面积。

**L0788**

```python
    dens_T = n_T / area_T if area_T > 0 else float("nan")
```

解释：T-zone 内死亡密度。

**L0789**

```python
    dens_out = n_out / area_out if area_out > 0 else float("nan")
```

解释：T-zone 外死亡密度。

**L0790**

```python
    ratio = dens_T / dens_out if dens_out > 0 else float("inf")
```

解释：T-zone 内外死亡密度比。

**L0791**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0792**

```python
    print("\nDeath spatial diagnostic")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0793**

```python
    print("------------------------")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0794**

```python
    print(f"deaths in T-zone       = {n_T} / {n_total}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0795**

```python
    print(f"deaths outside T-zone  = {n_out} / {n_total}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0796**

```python
    print(f"T-zone area            = {area_T:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0797**

```python
    print(f"outside area           = {area_out:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0798**

```python
    print(f"death density T-zone   = {dens_T:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0799**

```python
    print(f"death density outside  = {dens_out:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0800**

```python
    print(f"density ratio T/out    = {ratio:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。


### 第 801–850 行

**L0801**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0802**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0803**

```python
def pf_noise_diagnostic(
```

解释：定义函数：重复计算同一参数的粒子似然，估计 Monte Carlo 噪声。

**L0804**

```python
    deaths: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0805**

```python
    p: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0806**

```python
    T_end: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0807**

```python
    n_particles: int,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0808**

```python
    area_points: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0809**

```python
    mode: str,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0810**

```python
    sigma: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0811**

```python
    repeats: int = PF_NOISE_REPEATS,
```

解释：ParticleState 的字段 repeats，保存粒子状态的一部分。

**L0812**

```python
    label: str = "params",
```

解释：ParticleState 的字段 label，保存粒子状态的一部分。

**L0813**

```python
) -> np.ndarray:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0814**

```python
    """Repeat the same particle likelihood to estimate Monte Carlo noise."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0815**

```python
    lls = []
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0816**

```python
    start = time.time()
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0817**

```python
    for r in range(repeats):
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0818**

```python
        ll = particle_loglikelihood(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0819**

```python
            death_events=deaths,
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0820**

```python
            p=p,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0821**

```python
            T_end=T_end,
```

解释：观测窗口终点。

**L0822**

```python
            n_particles=n_particles,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0823**

```python
            area_points=area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0824**

```python
            seed=PF_SEED + 10000 + 1009 * r,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0825**

```python
            mode=mode,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0826**

```python
            sigma=sigma,
```

解释：soft indicator 的平滑尺度。

**L0827**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0828**

```python
        lls.append(ll)
```

解释：向列表末尾添加一个新元素；这里常用于记录新事件或新增圆盘。

**L0829**

```python
    arr = np.asarray(lls, dtype=float)
```

解释：把输入转换成 NumPy 数组，方便后续向量化计算。

**L0830**

```python
    elapsed = time.time() - start
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0831**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0832**

```python
    print(f"\nPF noise diagnostic at {label}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0833**

```python
    print("--------------------------------")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0834**

```python
    print(f"repeats = {repeats}, particles = {n_particles}, mode = {mode}, sigma = {sigma}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0835**

```python
    print(f"mean loglik = {np.mean(arr):.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0836**

```python
    print(f"std  loglik = {np.std(arr, ddof=1) if repeats > 1 else 0.0:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0837**

```python
    print(f"min  loglik = {np.min(arr):.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0838**

```python
    print(f"max  loglik = {np.max(arr):.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0839**

```python
    print(f"elapsed     = {elapsed:.1f} seconds")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0840**

```python
    return arr
```

解释：返回结果给调用这个函数的地方。

**L0841**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0842**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0843**

```python
def likelihood_profile_lambda_c(
```

解释：定义函数：固定其他参数，只扫描 lambda_a_c，查看一维似然剖面。

**L0844**

```python
    deaths: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0845**

```python
    true_params: ModelParams,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0846**

```python
    T_end: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0847**

```python
    area_points: np.ndarray,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0848**

```python
    n_particles: int,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0849**

```python
    mode: str,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0850**

```python
    sigma: float,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。


### 第 851–900 行

**L0851**

```python
) -> None:
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0852**

```python
    """Optional one-dimensional profile: vary lambda_a_c and keep lambda_a_T fixed."""
```

解释：单行文档字符串：说明当前模块/函数的用途。

**L0853**

```python
    grid = np.exp(np.linspace(math.log(0.005), math.log(0.5), PROFILE_GRID_SIZE))
```

解释：计算指数函数；这里通常是把 log 参数或 log 权重转回普通尺度。

**L0854**

```python
    print("\nLikelihood profile diagnostic: lambda_a_c")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0855**

```python
    print("-----------------------------------------")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0856**

```python
    print("lambda_a_c, loglik")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0857**

```python
    best_lc = None
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0858**

```python
    best_ll = -np.inf
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0859**

```python
    for lc in grid:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0860**

```python
        p_test = replace(true_params, lambda_a_c=float(lc))
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0861**

```python
        if not valid_params(p_test):
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0862**

```python
            continue
```

解释：跳过本轮循环剩余部分，进入下一轮循环。

**L0863**

```python
        ll = particle_loglikelihood(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0864**

```python
            death_events=deaths,
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0865**

```python
            p=p_test,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0866**

```python
            T_end=T_end,
```

解释：观测窗口终点。

**L0867**

```python
            n_particles=n_particles,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0868**

```python
            area_points=area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0869**

```python
            seed=PF_SEED + 424242,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0870**

```python
            mode=mode,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0871**

```python
            sigma=sigma,
```

解释：soft indicator 的平滑尺度。

**L0872**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0873**

```python
        print(f"{lc:.6g}, {ll:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0874**

```python
        if ll > best_ll:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0875**

```python
            best_ll = ll
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0876**

```python
            best_lc = float(lc)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0877**

```python
    print(f"profile best lambda_a_c = {best_lc:.6g}, loglik = {best_ll:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0878**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0879**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0880**

```python
# 8. Main demo
```

解释：主程序：把上面的模块串起来运行。

**L0881**

```python
# ============================================================
```

解释：分隔线注释：视觉上划分代码章节，没有执行效果。

**L0882**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0883**

```python
def print_param_table(true_p: ModelParams, estimated_p: ModelParams, keys: Sequence[str]) -> None:
```

解释：定义函数：打印真实参数和估计参数的对比表。

**L0884**

```python
    print("\nParameter comparison")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0885**

```python
    print("--------------------")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0886**

```python
    print(f"{'parameter':<14} {'true':>12} {'estimated':>12} {'ratio est/true':>16}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0887**

```python
    for key in keys:
```

解释：for 循环：依次遍历一个序列/数组/列表里的元素。

**L0888**

```python
        tv = getattr(true_p, key)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0889**

```python
        ev = getattr(estimated_p, key)
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0890**

```python
        print(f"{key:<14} {tv:12.5g} {ev:12.5g} {ev / tv:16.4g}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0891**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0892**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0893**

```python
def main() -> None:
```

解释：定义函数：主程序：模拟数据、诊断、估计参数、比较结果。

**L0894**

```python
    true_params = ModelParams(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0895**

```python
        lambda_a_1=5.00,
```

解释：caspase activation 的 dominating intensity，也是 active-zone 内强度上界。

**L0896**

```python
        lambda_a_T=0.50,
```

解释：T-zone 内背景 activation 强度。

**L0897**

```python
        lambda_a_c=0.05,
```

解释：T-zone 外背景 activation 强度。

**L0898**

```python
        lambda_d=1.00,
```

解释：死亡事件强度系数。

**L0899**

```python
        beta_a_R=2.50,
```

解释：activation 圆盘半径的指数分布 rate。

**L0900**

```python
        beta_a_T=1.20,
```

解释：activation center 的过期 rate。


### 第 901–950 行

**L0901**

```python
        beta_d_R=2.00,
```

解释：ERK 保护圆盘半径的指数分布 rate。

**L0902**

```python
        beta_d_T=0.80,
```

解释：ERK 保护区域的过期 rate。

**L0903**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0904**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0905**

```python
    print("Simulating synthetic death events...")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0906**

```python
    sim = simulate_death_events(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0907**

```python
        true_params,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0908**

```python
        T_max=T_MAX,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0909**

```python
        target_deaths=TARGET_DEATHS,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0910**

```python
        seed=123,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0911**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0912**

```python
    deaths = sim["death_events"]
```

解释：死亡事件数组。

**L0913**

```python
    final_time = float(sim["final_time"][0])
```

解释：模拟最终时间。

**L0914**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0915**

```python
    if len(deaths) == 0:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0916**

```python
        print("No deaths simulated. Increase T_MAX or change parameters.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0917**

```python
        return
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0918**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0919**

```python
    np.savetxt(
```

解释：把模拟得到的死亡事件保存成 CSV 文件，方便之后查看或复用。

**L0920**

```python
        "simulated_death_events.csv",
```

解释：把模拟得到的死亡事件保存成 CSV 文件，方便之后查看或复用。

**L0921**

```python
        deaths,
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0922**

```python
        delimiter=",",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0923**

```python
        header="x,y,t",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0924**

```python
        comments="",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0925**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0926**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0927**

```python
    # If we simulate a fixed physical observation window, the endpoint is T_MAX.
```

解释：注释：If we simulate a fixed physical observation window, the endpoint is T_MAX.。

**L0928**

```python
    # If we stop at a target number of deaths, the endpoint is the stopping time.
```

解释：注释：If we stop at a target number of deaths, the endpoint is the stopping time.。

**L0929**

```python
    if TARGET_DEATHS is None:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0930**

```python
        T_end = T_MAX
```

解释：观测窗口终点。

**L0931**

```python
    else:
```

解释：否则分支：前面条件都不成立时执行这里。

**L0932**

```python
        T_end = final_time
```

解释：观测窗口终点。

**L0933**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0934**

```python
    print(f"  simulated deaths: {len(deaths)}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0935**

```python
    print(f"  raw simulator final time = {final_time:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0936**

```python
    print(f"  observation endpoint T_end = {T_end:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0937**

```python
    print(f"  crude full-area rate n/(|W|T) = {len(deaths)/(AREA_W*T_end):.5g}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0938**

```python
    print("  saved: simulated_death_events.csv")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L0939**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0940**

```python
    if RUN_DEATH_SPATIAL_DIAGNOSTIC:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0941**

```python
        death_spatial_diagnostic(deaths)
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0942**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0943**

```python
    # Use a fixed set of quadrature points for diagnostics and for comparable log-likelihood calls.
```

解释：注释：Use a fixed set of quadrature points for diagnostics and for comparable log-似然 calls.。

**L0944**

```python
    rng_area = np.random.default_rng(AREA_SEED)
```

解释：创建 NumPy 随机数生成器；给定 seed 可让结果可重复。

**L0945**

```python
    diagnostic_area_points = np.column_stack([
```

解释：固定的一批面积积分点，用来保证不同参数比较时更公平。

**L0946**

```python
        rng_area.uniform(0.0, Lx, AREA_MC_POINTS),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0947**

```python
        rng_area.uniform(0.0, Ly, AREA_MC_POINTS),
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0948**

```python
    ])
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L0949**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0950**

```python
    if RUN_PF_NOISE_DIAGNOSTIC:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。


### 第 951–1000 行

**L0951**

```python
        pf_noise_diagnostic(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0952**

```python
            deaths=deaths,
```

解释：死亡事件数组。

**L0953**

```python
            p=true_params,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0954**

```python
            T_end=T_end,
```

解释：观测窗口终点。

**L0955**

```python
            n_particles=N_PARTICLES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0956**

```python
            area_points=diagnostic_area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0957**

```python
            mode=LIKELIHOOD_MODE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0958**

```python
            sigma=SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0959**

```python
            repeats=PF_NOISE_REPEATS,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0960**

```python
            label="true params before optimization",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0961**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0962**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0963**

```python
    if RUN_LIKELIHOOD_PROFILE:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L0964**

```python
        likelihood_profile_lambda_c(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0965**

```python
            deaths=deaths,
```

解释：死亡事件数组。

**L0966**

```python
            true_params=true_params,
```

解释：模拟数据时使用的真实参数。

**L0967**

```python
            T_end=T_end,
```

解释：观测窗口终点。

**L0968**

```python
            area_points=diagnostic_area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0969**

```python
            n_particles=N_PARTICLES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0970**

```python
            mode=LIKELIHOOD_MODE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0971**

```python
            sigma=SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0972**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0973**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0974**

```python
    # Base parameters: fixed values for non-estimated parameters.
```

解释：注释：Base parameters: fixed values for non-estimated parameters.。

**L0975**

```python
    # In real use, replace true_params below by your chosen fixed/default values.
```

解释：注释：In real use, replace true_params below by your chosen fixed/default values.。

**L0976**

```python
    base_params = true_params
```

解释：没有被估计的参数固定在这里。

**L0977**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L0978**

```python
    estimated_params, best_loglik = fit_parameters(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0979**

```python
        death_events=deaths,
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0980**

```python
        base_params=base_params,
```

解释：没有被估计的参数固定在这里。

**L0981**

```python
        keys=ESTIMATE_KEYS,
```

解释：要估计的参数名。

**L0982**

```python
        T_end=T_end,
```

解释：观测窗口终点。

**L0983**

```python
        n_particles=N_PARTICLES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0984**

```python
        area_mc_points=AREA_MC_POINTS,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0985**

```python
        pf_seed=PF_SEED,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0986**

```python
        pf_replicates=PF_REPLICATES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0987**

```python
        resample_method=RESAMPLE_METHOD,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0988**

```python
        mode=LIKELIHOOD_MODE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0989**

```python
        sigma=SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L0990**

```python
        maxiter=OPT_MAXITER,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0991**

```python
        popsize=OPT_POPSIZE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0992**

```python
        polish=POLISH_WITH_LBFGSB,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0993**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L0994**

```python
    ll_true = particle_loglikelihood(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L0995**

```python
        death_events=deaths,
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L0996**

```python
        p=true_params,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0997**

```python
        T_end=T_end,
```

解释：观测窗口终点。

**L0998**

```python
        n_particles=N_PARTICLES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L0999**

```python
        area_points=diagnostic_area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1000**

```python
        seed=PF_SEED + 999,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。


### 第 1001–1050 行

**L1001**

```python
        mode=LIKELIHOOD_MODE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1002**

```python
        sigma=SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L1003**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L1004**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1005**

```python
    ll_est = particle_loglikelihood(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L1006**

```python
        death_events=deaths,
```

解释：观测到的死亡事件数组，列为 x,y,t。

**L1007**

```python
        p=estimated_params,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1008**

```python
        T_end=T_end,
```

解释：观测窗口终点。

**L1009**

```python
        n_particles=N_PARTICLES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1010**

```python
        area_points=diagnostic_area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1011**

```python
        seed=PF_SEED + 999,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1012**

```python
        mode=LIKELIHOOD_MODE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1013**

```python
        sigma=SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L1014**

```python
    )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L1015**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1016**

```python
    print("\nDiagnostic log-likelihood comparison")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1017**

```python
    print("------------------------------------")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1018**

```python
    print(f"loglik at true params      = {ll_true:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1019**

```python
    print(f"loglik at estimated params = {ll_est:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1020**

```python
    print(f"difference est - true      = {ll_est - ll_true:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1021**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1022**

```python
    if RUN_PF_NOISE_DIAGNOSTIC:
```

解释：条件判断：如果这个条件成立，就执行缩进在下面的代码块。

**L1023**

```python
        pf_noise_diagnostic(
```

解释：函数调用开始：下面几行会继续填写这个函数的参数。

**L1024**

```python
            deaths=deaths,
```

解释：死亡事件数组。

**L1025**

```python
            p=estimated_params,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1026**

```python
            T_end=T_end,
```

解释：观测窗口终点。

**L1027**

```python
            n_particles=N_PARTICLES,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1028**

```python
            area_points=diagnostic_area_points,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1029**

```python
            mode=LIKELIHOOD_MODE,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1030**

```python
            sigma=SOFT_SIGMA,
```

解释：soft indicator 的平滑尺度。

**L1031**

```python
            repeats=PF_NOISE_REPEATS,
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1032**

```python
            label="estimated params after optimization",
```

解释：赋值语句：计算右边表达式，并把结果保存到左边变量中。

**L1033**

```python
        )
```

解释：括号/列表/字典结束：结束前面多行函数调用或数据结构。

**L1034**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1035**

```python
    print_param_table(true_params, estimated_params, ESTIMATE_KEYS)
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。

**L1036**

```python
    print(f"\nBest estimated particle log-likelihood: {best_loglik:.4f}")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1037**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1038**

```python
    print("\nEstimated full parameter object:")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1039**

```python
    print(estimated_params)
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1040**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1041**

```python
    print("\nNotes:")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1042**

```python
    print("  1. If PF noise std is large compared with est-true loglik difference,")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1043**

```python
    print("     increase N_PARTICLES and PF_REPLICATES before interpreting the MLE.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1044**

```python
    print("  2. Fixed-time simulation is recommended for cleaner point-process likelihood.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1045**

```python
    print("  3. Try smaller SOFT_SIGMA, then LIKELIHOOD_MODE='exact' after the soft version works.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1046**

```python
    print("  4. For redistribution, RESAMPLE_METHOD='residual_systematic' combines residual")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1047**

```python
    print("     resampling with Kitagawa/systematic positions; change it for comparisons.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1048**

```python
    print("  5. Death-only data may not identify all caspase and ERK parameters at once;")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1049**

```python
    print("     estimate a small subset first, then enlarge ESTIMATE_KEYS.")
```

解释：打印信息到控制台，方便观察程序运行状态或诊断结果。

**L1050**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。


### 第 1051–1053 行

**L1051**

```python

```

解释：空行：用于分隔代码块，让程序结构更清楚；Python 会忽略空行。

**L1052**

```python
if __name__ == "__main__":
```

解释：Python 脚本入口判断：只有直接运行这个文件时才执行 main()，被 import 时不自动运行。

**L1053**

```python
    main()
```

解释：普通代码行：属于当前函数/代码块的一步操作，具体作用要结合上下文理解。


---

## 建议学习顺序

先不要从第 1 行硬背到最后。建议按这个顺序：`ModelParams/ParticleState` → 几何函数 → `simulate_death_events` → `propagate_hidden_until` → `particle_loglikelihood` → 重采样函数 → `fit_parameters` → `main`。

真正最核心的是：`particle_loglikelihood` 每看到一个死亡事件，就让所有粒子先从上一个死亡时间传播到这次死亡时间，然后用这次死亡点的条件强度更新权重，再必要时重采样。
