# pf_mle_caspase_erk_TINY_TEST.py 中文逐行讲解

这份讲义按原文件行号解释。空行、纯分隔线以及同一条语句拆成多行的部分会合并说明；其余每一条真正执行的语句都覆盖到了。

## 0. 先用一句话说清整段代码

这份程序先用一组已知的“真实参数”模拟 8 个细胞死亡事件，然后假装只观察到了这些死亡事件，用粒子滤波近似死亡数据的似然，最后用差分进化算法估计两个隐藏激活参数：

\[
\lambda_{a,T},\qquad \lambda_{a,c}.
\]

这里：

- \(V_t^a\)：隐藏的 caspase 激活圆盘集合；
- \(V_t^d\)：已经观察到的死亡事件；
- \(V_t^p\)：隐藏的 ERK 保护圆盘集合；
- 一个位置只有在“被激活且未被保护”时才可能死亡。

程序实际上包含两个不同任务：

1. **模拟器**：已知参数，生成假数据；
2. **推断器**：只拿死亡假数据，反过来估计参数。

不要把这两部分混为一谈。

## 1. 整体调用顺序

程序从最后两行开始执行：

1. 第 946–947 行调用 main；
2. main 调用 simulate_death_events，生成死亡数据；
3. main 调用 fit_parameters；
4. fit_parameters 反复调用 objective；
5. objective 每次尝试一组参数，并调用 particle_loglikelihood；
6. particle_loglikelihood 为每个死亡区间调用 propagate_hidden_until；
7. 粒子对该组参数给出一个近似对数似然；
8. differential_evolution 寻找让对数似然最大的参数。

## 2. 读代码前必须认识的 Python 写法

### 2.1 缩进

Python 用缩进表示“属于谁”。例如：

    if condition:
        do_something()

第二行缩进了，所以只在 condition 成立时执行。

### 2.2 冒号类型标注

    x: float

表示作者预期 x 是浮点数。它主要帮助阅读和静态检查，通常不会在运行时自动阻止错误类型。

### 2.3 箭头返回类型

    def f(x: float) -> bool:

表示 f 接收浮点数，预期返回布尔值 True 或 False。

### 2.4 常见符号

- =：赋值；
- ==：判断两边是否相等；
- <=：小于等于；
- **：乘方，例如 r ** 2 是 \(r^2\)；
- and、or、not：逻辑“且、或、非”；
- None：没有值；
- A | None：值可以是 A 类型，也可以是 None；
- []：列表，或数组索引；
- ()：函数调用或元组；
- {}：字典；
- f"..."：格式化字符串，可把变量值放进文字；
- #：从这里到本行末尾都是注释，不执行。

### 2.5 数组切片

如果 deaths 的每行是 \((x,y,t)\)，那么：

    deaths[:, 2]

含义是“取所有行的第 3 列”。Python 从 0 开始计数，所以 2 是第三列。

### 2.6 列表推导式

    [f(i) for i in range(n)]

等价于循环 n 次，把每次的 f(i) 放进一个列表。

## 3. 第 1–49 行：文件说明和导入

### 第 1–36 行

最外面的三引号文字是模块文档字符串。它不参与模型计算，只是说明文件用途。

- 第 2–3 行：标题是“观测驱动的 caspase–ERK 点过程模型的粒子滤波极大似然”。
- 第 5–8 行：说明三个过程：隐藏激活、观测死亡、死亡后触发的隐藏 ERK 保护。
- 第 10–16 行：指出严格状态应写成

\[
Z_t=(V_t^a,V_t^p,V_{0:t}^d).
\]

死亡历史 \(V_{0:t}^d\) 是所有粒子都共同知道的观测量，因此 ParticleState 只保存每个粒子各自不同的 \(V_t^a,V_t^p\)。

- 第 18–20 行：程序先模拟数据，再做参数估计。
- 第 22–29 行：硬指示函数容易让所有粒子权重变成接近 0，因此提供 soft 模式。
- 第 31–35 行：依赖 NumPy、SciPy，并给出运行命令。这里写的文件名和当前附件名不一致，但不影响程序内部运行。

### 第 38 行

    from __future__ import annotations

让类型标注延迟解析。这样诸如 np.ndarray | None 一类标注更容易兼容，也不会在函数定义时急着计算所有类型对象。

### 第 40 行

    from dataclasses import dataclass, replace

- dataclass：自动生成初始化函数、打印表示等；
- replace：复制一个 dataclass 对象，同时替换指定字段。

### 第 41 行

    from typing import Dict, Iterable, List, Sequence, Tuple

导入类型标注：

- Dict：字典；
- Iterable：可迭代对象，本文件实际上没有使用；
- List：列表；
- Sequence：序列；
- Tuple：元组。

### 第 42–44 行

- import math：数学函数，如 log、sqrt；
- import time：计时；
- import numpy as np：把 NumPy 简写为 np。

### 第 46–49 行

程序尝试从 scipy.optimize 导入：

- differential_evolution：全局随机优化；
- minimize：局部最小化，这里用于可选的 L-BFGS-B。

若导入失败，就抛出更清楚的 ImportError，并保留原始异常作为原因。pragma: no cover 只是覆盖率测试提示，不影响执行。

## 4. 第 51–101 行：全局设置

### 第 55–58 行：空间窗口

    Lx = 10.0
    Ly = 10.0
    AREA_W = Lx * Ly

定义

\[
W=[0,10]\times[0,10],\qquad |W|=100.
\]

AREA_W 是整个空间面积。

### 第 60–64 行：T 形区域边界

- x1 = 10/3；
- x2 = 20/3；
- y1 = 10/3；
- y2 = 20/3。

后面用这些边界拼出 T-zone：中间竖条加左侧横臂。

### 第 69–71 行：观察终止规则

    USE_FIXED_TIME_WINDOW = False
    T_MAX = 5.0
    TARGET_DEATHS = None if USE_FIXED_TIME_WINDOW else 8

因为 USE_FIXED_TIME_WINDOW=False，所以条件表达式选择 else，最终：

    TARGET_DEATHS = 8

模拟会在“达到 8 次死亡”或“时间超过 5”中的先到者停止。

如果改成 True，则 TARGET_DEATHS=None，表示不限定死亡个数，只观察固定时间 \([0,5]\)。

### 第 75 行

    N_PARTICLES = 20

粒子滤波使用 20 个粒子。这只是 tiny test，正式估计通常太少。

### 第 76 行

    AREA_MC_POINTS = 50

用 50 个固定均匀点近似“激活但未保护区域”的面积。也是很小的测试配置。

### 第 77 行

    RESAMPLE_THRESHOLD = 0.5

当

\[
N_{\mathrm{eff}}<0.5N
\]

时重采样。这里 \(N=20\)，所以阈值是 10。

### 第 78 行

    PF_REPLICATES = 1

每组候选参数只运行一次粒子滤波。若设为 3，就用 3 次近似对数似然的平均值作为优化目标。

### 第 79–80 行

- PF_SEED：粒子滤波随机种子；
- AREA_SEED：面积积分点随机种子。

固定种子使结果可复现，并让不同参数使用同一批积分点，减少比较时的额外随机波动。

### 第 84–86 行

- LIKELIHOOD_MODE="soft"：当前用平滑覆盖概率，不用硬 0/1；
- SOFT_SIGMA=0.10：边界平滑宽度；
- MIN_EVENT_INTENSITY=1e-12：防止 log(0)。

注意：soft 模式不仅是计算技巧，它确实把原模型的硬指示函数改成了一个近似模型。

### 第 89–91 行

- OPT_MAXITER=2：差分进化最多 2 代；
- OPT_POPSIZE=3：种群规模乘子；
- POLISH_WITH_LBFGSB=False：不做最后的局部优化。

这些都为了快速测试，不是正式拟合配置。

### 第 94–98 行

- RUN_DEATH_SPATIAL_DIAGNOSTIC=True：打印 T-zone 空间诊断；
- RUN_PF_NOISE_DIAGNOSTIC=False：不重复评估粒子噪声；
- PF_NOISE_REPEATS=3：若开启则重复 3 次；
- RUN_LIKELIHOOD_PROFILE=False：不画一维似然剖面；
- PROFILE_GRID_SIZE=15：若开启则测试 15 个网格值。

### 第 101 行

    ESTIMATE_KEYS = ("lambda_a_T", "lambda_a_c")

只估计 T-zone 内外两个背景激活率。其他六个参数固定在 base_params 中。

末尾逗号和圆括号说明这是一个二元素元组。

## 5. 第 108–174 行：参数对象、粒子状态与参数变换

### 第 108–124 行：ModelParams

@dataclass(frozen=True) 自动生成构造函数，并模拟“不可修改”对象。

因此可以写：

    p = ModelParams(lambda_d=2.0)

但不能直接写 p.lambda_d=3.0。要修改时用 replace 创建新对象。

八个字段含义：

- 第 111 行 lambda_a_1：激活区内的激活强度，也是 thinning 的支配强度；
- 第 112 行 lambda_a_T：T-zone 内背景激活强度；
- 第 113 行 lambda_a_c：T-zone 外背景激活强度；
- 第 116 行 lambda_d：激活且未保护区域上的单位面积死亡强度；
- 第 119 行 beta_a_R：激活半径指数分布的率；
- 第 120 行 beta_a_T：每个激活中心消失的率；
- 第 123 行 beta_d_R：ERK 半径指数分布的率；
- 第 124 行 beta_d_T：每个 ERK 区域消失的率。

例如

\[
R^a\sim \operatorname{Exp}(\beta_{a,R})
\]

的均值是 \(1/\beta_{a,R}\)。

### 第 127–131 行：ParticleState

@dataclass 自动生成 ParticleState(active, erk)。

- active：当前仍存在的激活圆盘列表；
- erk：当前仍存在的 ERK 保护圆盘列表；
- 每个元素是 \((x,y,r)\)：圆心坐标和半径。

这个类不是 frozen，因为传播粒子时要 append 和 pop。

### 第 134–135 行：clone_state

    return ParticleState(active=list(st.active), erk=list(st.erk))

创建两个新列表，复制粒子状态。

为什么不能直接返回 st？因为重采样后多个后代可能来自同一个祖先；如果它们共享同一列表，修改一个粒子会同时修改其他粒子。

元组 \((x,y,r)\) 本身不可变，所以复制列表已经足够。

### 第 138–145 行：valid_params

- 第 139–142 行：把八个数放进 vals；
- 第 143 行：检查所有值有限且严格大于 0；
- 第 144 行：若有 NaN、无穷或非正数，返回 False；
- 第 145 行：还要求

\[
\lambda_{a,c}\leq \lambda_{a,T}\leq \lambda_{a,1}.
\]

这既符合模型设定，也保证 thinning 接受率不超过 1。

### 第 148–159 行：PARAM_BOUNDS

字典把每个参数名映射到原始尺度的下界和上界。

例如：

    "lambda_a_T": (0.02, 2.0)

表示优化只允许 \(0.02\leq\lambda_{a,T}\leq2\)。

### 第 162–166 行：unpack_log_params

输入：

- log_vec：优化器给出的对数参数向量；
- base：未估计参数的基准对象；
- keys：要替换哪些参数。

执行过程：

1. p=base，先从完整基准参数开始；
2. zip(keys, log_vec) 把参数名和对应数值配对；
3. np.exp(log_value) 从对数尺度恢复正参数；
4. replace(p, **{key: value}) 复制 p，并只替换该字段；
5. 返回完整参数对象。

双星号 ** 把字典拆成关键字参数。例如：

    **{"lambda_d": 2.0}

相当于：

    lambda_d=2.0

### 第 169–170 行：pack_log_params

这是上一个函数的反方向：

1. getattr(p,key) 按字符串名字读取字段；
2. math.log 取自然对数；
3. 组成浮点 NumPy 数组。

本文件定义了它，但后面没有实际调用。

### 第 173–174 行：log_bounds

把原始尺度边界 \((L,U)\) 转成：

\[
(\log L,\log U).
\]

因为优化器实际搜索的是对数参数。

## 6. 第 181–291 行：几何与 soft 指示函数

### 第 181–184 行：is_inside_T_zone

- 第 182 行判断点是否在中间竖条；
- 第 183 行判断点是否在左侧横臂；
- 第 184 行只要满足任意一个，就属于 T-zone。

对应面积是：

\[
(x_2-x_1)L_y+x_1(y_2-y_1)=44.4444\ldots
\]

两个矩形只在边界接触，没有重复正面积。

### 第 187–191 行：inside_union_exact

逐个检查圆盘：

\[
(x-c_x)^2+(y-c_y)^2\leq r^2.
\]

只要点落在任意一个圆盘内，立刻返回 True；循环结束仍未命中则返回 False。

因此它计算的是硬指示函数：

\[
\mathbf 1\{(x,y)\in\cup_j B(c_j,r_j)\}.
\]

### 第 194–199 行：local_activation_intensity

按优先级返回局部激活强度：

1. 已在某个 active 圆盘里：lambda_a_1；
2. 否则若在 T-zone：lambda_a_T；
3. 否则：lambda_a_c。

也就是激活会在已有激活区内自增强。

### 第 202–203 行：_sigmoid_clipped

计算：

\[
\sigma(z)=\frac{1}{1+e^{-z}}.
\]

np.clip 把 z 限制在 \([-50,50]\)，避免 exp 发生数值上溢。

函数名前的单下划线表示“内部辅助函数”，不是强制私有。

### 第 206–225 行：soft_union_probability_points

输入 points 的形状是 \((M,2)\)，M 是积分点数；输出长度为 M。

- 第 216 行：n=M；
- 第 217–218 行：若没有圆盘，所有点覆盖概率都返回 0；
- 第 219 行：先把每个点的最佳边界分数设为极小值；
- 第 220–221 行：分别取全部 x 坐标和 y 坐标；
- 第 222 行：遍历每个圆盘；
- 第 223 行：向量化计算所有 M 个点到该圆心的距离；
- 第 224 行：保留所有圆盘中最大的 \(r-\text{distance}\)；
- 第 225 行：返回

\[
\operatorname{sigmoid}\left(
\frac{\max_j\{r_j-\|x-c_j\|\}}{\sigma}
\right).
\]

点在圆内时 \(r-d>0\)，结果大于 0.5；在边界上等于 0.5；圆外小于 0.5。

这里名字 probability 是建模上的平滑解释，并不是从某个真实随机圆盘模型严格推导出的概率。

### 第 228–240 行：soft_union_probability_one

与上一个函数数学相同，但只处理单个位置 \((x,y)\)：

- 空圆盘集合返回 0；
- best 保存最大的 \(r-d\)；
- math.sqrt 计算单个距离；
- 最后返回一个普通 Python float。

### 第 243–269 行：active_unprotected_area

目标是近似：

\[
\left|A(V^a)\setminus A(V^p)\right|.
\]

area_points 是预先均匀抽取的 M 个空间点。

#### 第 249 行

原始字符串文档说明用固定 Monte Carlo 积分点近似面积。前缀 r 让反斜杠按普通字符处理。

#### 第 250–251 行

没有 active 圆盘时，激活未保护面积必为 0，立即返回。

#### 第 253–262 行：exact 模式

- active：M 个布尔值，初始全 False；
- protected：M 个布尔值，初始全 False；
- px、py：全部积分点坐标；
- 第 258–259 行：对每个 active 圆盘，用按位或 |= 累积“是否被任一 active 圆盘覆盖”；
- 第 260–261 行：同理得到保护指示；
- ~protected：逻辑非，即未保护；
- active & (~protected)：激活且未保护；
- np.mean：满足条件的积分点比例；
- 再乘 AREA_W，得到面积估计：

\[
\widehat{|D|}
=|W|\frac1M\sum_{m=1}^M\mathbf1\{U_m\in D\}.
\]

#### 第 264–267 行：soft 模式

把两个硬布尔量换成 \(p_a,p_p\in[0,1]\)，用：

\[
|W|\frac1M\sum_m p_a(U_m)\,[1-p_p(U_m)].
\]

#### 第 269 行

mode 既不是 exact 也不是 soft 时主动报错，避免静默使用错误模式。

### 第 272–291 行：death_event_intensity

这个函数计算观测死亡发生前一刻的空间点强度：

\[
\lambda_\theta^d(x,y,s\mid Z_{s-}).
\]

#### 第 282–284 行：exact

检查死亡位置是否：

1. 位于 active 并集；
2. 不位于 ERK 并集。

若成立返回 lambda_d，否则返回 1e-12。

严格硬模型本应在不成立时返回 0；这里用极小正数只是为了避免后面 math.log(0) 报错。所以代码中的 exact 仍带有数值下限。

#### 第 286–289 行：soft

计算：

\[
\max\left\{
\varepsilon,\,
\lambda_d\,p_a(x,y)\,[1-p_p(x,y)]
\right\}.
\]

#### 第 291 行

未知模式报 ValueError。

## 7. 第 298–372 行：Gillespie 合成数据模拟器

### 第 298–303 行：函数签名

simulate_death_events 接收：

- p：完整模型参数；
- T_max：最大模拟时间；
- target_deaths：目标死亡数，也可以为 None；
- seed：随机种子。

返回一个字典，字典的值都是 NumPy 数组。

默认参数在函数定义时取当时的 T_MAX 和 TARGET_DEATHS。

### 第 304–306 行

文档字符串说明返回死亡事件和隐藏历史。若参数无效，立即抛出 ValueError，不继续模拟。

### 第 308 行

    rng = np.random.default_rng(seed)

创建独立随机数生成器。相同 seed 会复现同一条模拟路径。

### 第 309–313 行

- st：初始没有 active 和 ERK 圆盘；
- t=0：从时间 0 开始；
- cas_events：记录被接受的激活事件 \((x,y,t)\)；
- death_events：记录死亡事件 \((x,y,t)\)。

### 第 315 行：主循环条件

只要同时满足：

1. t<T_max；
2. target_deaths 为 None，或者死亡数还没达到目标；

就继续。

### 第 316–317 行

读取当前 active 圆盘数和 ERK 圆盘数。

### 第 319–322 行：四类候选事件总率

\[
\begin{aligned}
a_{\mathrm{act}}&=\lambda_{a,1}|W|,\\
a_{\mathrm{death}}&=\lambda_d|W|,\\
a_{\mathrm{act-exp}}&=n_a\beta_{a,T},\\
a_{\mathrm{erk-exp}}&=n_p\beta_{d,T}.
\end{aligned}
\]

前两个是支配 Poisson 候选率，之后还要 thinning；后两个是所有独立指数寿命时钟叠加后的总率。

### 第 324–326 行

a0 是四类率之和。若总率不正，就没有任何事件可能发生，退出循环。

在当前 valid_params 约束下前两个率为正，因此这条主要是安全保护。

### 第 328 行：下一事件等待时间

    t += rng.exponential(1.0 / a0)

若总事件率为 \(a_0\)，等待时间：

\[
\Delta t\sim\operatorname{Exp}(a_0),
\qquad E[\Delta t]=1/a_0.
\]

NumPy exponential 接收的是 scale，也就是均值 \(1/a_0\)，所以代码传 1.0/a0。

### 第 329–330 行

若新事件时间已经超过 T_max，则该事件不在观察窗口中，退出。

### 第 332–335 行：选择事件类型

- u 是 \([0,1)\) 均匀随机数；
- pa 是激活候选占总率比例；
- pd 是死亡候选占总率比例；
- pe 是 active 消失占总率比例；
- 剩余概率自动对应 ERK 消失。

### 第 337–345 行：激活候选

若 u 落在第一个概率区间：

1. 在 W 内均匀抽位置 \((x,y)\)；
2. 计算该点真正局部激活率 lam；
3. 以 lam/lambda_a_1 接受；
4. 接受后抽半径

\[
R^a\sim\operatorname{Exp}(\beta_{a,R});
\]

5. 把圆盘加入当前状态；
6. 把激活事件位置和时间记入 cas_events。

为什么接受率是 lam/lambda_a_1？候选空间强度为 lambda_a_1，thinning 后有效强度为：

\[
\lambda_{a,1}\times\frac{\lambda_{\mathrm{local}}}{\lambda_{a,1}}
=\lambda_{\mathrm{local}}.
\]

### 第 347–354 行：死亡候选

若 u 落在第二个概率区间：

1. 均匀抽候选死亡位置；
2. 只有位于 active 且不在 ERK 时接受；
3. 接受后记录死亡；
4. 抽 ERK 半径 \(R^d\sim\operatorname{Exp}(\beta_{d,R})\)；
5. 立即在死亡点加入保护圆盘。

候选总率是 lambda_d × AREA_W；空间均匀并用区域指示接受后，真正总死亡率成为：

\[
\lambda_d\,|A(V^a)\setminus A(V^p)|.
\]

### 第 356–360 行：active 消失

若 u 落在第三个区间：

- 只要 active 列表非空，就均匀选一个索引；
- pop 删除该圆盘。

因为每个圆盘都有相同消失率 beta_a_T，所以在“发生一次 active 消失”条件下，被删除者均匀分布。

### 第 362–366 行：ERK 消失

剩余情况对应 ERK 消失；同理均匀选一个现存 ERK 圆盘并删除。

### 第 368–372 行：返回

返回字典：

- death_events：形状通常为 \((n_d,3)\)，列为 x、y、t；
- cas_events：隐藏激活事件；
- final_time：把标量 t 包成长度 1 的数组。

final_time 做成数组不是必需的；直接返回 float 会更自然，但当前写法后面按 sim["final_time"][0] 读取。

## 8. 第 379–452 行：在两个死亡时刻之间传播隐藏状态

这是整份代码最关键的函数之一。

### 第 379–388 行：函数输入与输出

propagate_hidden_until 接收：

- st：某一个粒子的当前隐藏状态，函数会直接修改它；
- t0、t1：区间起点和终点；
- p：候选参数；
- rng：随机数生成器；
- area_points：固定面积积分点；
- mode、sigma：硬/软似然及平滑宽度。

返回的不是新状态，因为 st 已经被原地修改；返回值是这一段“没有观测到死亡”的对数生存因子：

\[
-\int_{t_0}^{t_1}
\lambda_d\,|A(V_s^a)\setminus A(V_s^p)|\,ds.
\]

### 第 389–400 行：文档字符串

这里明确区分：

- 隐藏激活、active 消失、ERK 消失：要在粒子中模拟；
- 死亡：已经观察到，不能再自由模拟。

观测点过程似然在一个区间内由两部分组成：

\[
\exp\left(-\int\lambda_s\,ds\right)
\prod_j \lambda_{s_j}.
\]

本函数负责前面的指数生存项；death_event_intensity 负责事件时刻的强度项。

### 第 401–402 行

- t 从 t0 开始；
- log_survival 初值为 0，因为乘法单位元 1 的对数是 0。

### 第 404–406 行

只要还没到 t1 就继续，并在每次迭代读取当前 active、ERK 数量。

### 第 408–411 行：隐藏事件率

这里故意没有 death_proposal_rate，因为死亡不是隐藏事件。

\[
a_{\mathrm{hidden}}
=\lambda_{a,1}|W|
+n_a\beta_{a,T}
+n_p\beta_{d,T}.
\]

### 第 413–415 行：当前死亡 hazard

先近似当前激活未保护面积 death_area，再计算整个空间的总死亡强度：

\[
h_s=\lambda_d\,\text{death\_area}.
\]

在下一次隐藏跳跃前，粒子状态不变，所以这段时间内 h_s 也保持不变。

### 第 417–419 行

若没有隐藏事件可能发生，状态会一直保持到 t1，因此把剩余区间的积分一次算完：

\[
\log S\leftarrow\log S-h_s(t_1-t).
\]

然后退出。

### 第 421 行

抽下一次隐藏事件等待时间：

\[
\Delta t\sim\operatorname{Exp}(a_{\mathrm{hidden}}).
\]

### 第 422–425 行

若下一隐藏事件在 t1 之后，则 \([t,t_1]\) 内没有隐藏跳跃：

1. 积累剩余区间的负 hazard 积分；
2. 令 t=t1；
3. 退出循环。

### 第 427–428 行

若隐藏事件确实在区间内：

\[
\log S\leftarrow\log S-h_s\Delta t,
\qquad
t\leftarrow t+\Delta t.
\]

这就是对分段常数 hazard 的精确时间积分；空间面积本身仍由 Monte Carlo 点近似。

### 第 430–432 行

抽均匀数 u，并计算隐藏事件中：

- 激活候选的概率 pa；
- active 消失的概率 pe；
- 剩余概率是 ERK 消失。

### 第 434–440 行：隐藏激活

逻辑与模拟器第 337–345 行相同：

1. 均匀抽空间位置；
2. 算局部激活率；
3. 以 lam/lambda_a_1 thinning；
4. 接受后抽半径并加入 st.active。

这里不记录 cas_events，因为粒子状态列表本身已经携带当前隐藏信息，似然计算不需要输出完整激活事件表。

### 第 442–445 行：active 消失

若发生 active expiration，均匀选一个现存 active 圆盘删除。

### 第 447–450 行：ERK 消失

剩余事件类型是 ERK expiration，均匀选一个现存 ERK 圆盘删除。

### 第 452 行

返回整个 \([t_0,t_1]\) 的对数生存项 log_survival。

## 9. 第 455–468 行：数值稳定求和与系统重采样

### 第 455–459 行：logsumexp_np

目标是稳定计算：

\[
\log\sum_i e^{a_i}.
\]

直接算 exp(a_i) 可能上溢或下溢。令

\[
m=\max_i a_i,
\]

则：

\[
\log\sum_i e^{a_i}
=m+\log\sum_i e^{a_i-m}.
\]

因为每个 \(a_i-m\leq0\)，指数不会上溢。

逐行解释：

- 第 456 行：取最大值并转成 Python float；
- 第 457–458 行：若最大值不是有限数，返回负无穷；
- 第 459 行：使用上面的稳定恒等式。

这里假定数组不为空；粒子数至少为 1。

### 第 462–468 行：systematic_resample

输入是归一化权重：

\[
w_i\geq0,\qquad \sum_iw_i=1.
\]

输出是 n 个祖先索引。

#### 第 464 行

n 是粒子数。

#### 第 465 行

先抽一个 \(U\sim U(0,1)\)，构造：

\[
u_j=\frac{U+j}{n},\qquad j=0,\ldots,n-1.
\]

因此 n 个点间距都是 \(1/n\)，只随机移动整体起点。

#### 第 466 行

cumsum 得到累计权重：

\[
(w_1,\;w_1+w_2,\;\ldots,\;1).
\]

#### 第 467 行

由于浮点误差，累计和最后一项可能是 0.9999999998；强行设为 1，避免最后一个位置越界。

#### 第 468 行

np.searchsorted 对每个位置 u_j 找到它落在哪个累计权重区间，返回对应祖先索引。

例如权重为 \((0.1,0.7,0.2)\)，累计权重为 \((0.1,0.8,1)\)。位置 0.4 落在第二段，所以选择祖先 1。索引从 0 开始。

side="right" 表示若位置刚好等于某个累计边界，就放到右侧区间。

## 10. 第 471–560 行：粒子滤波近似对数似然

### 第 471–482 行：函数签名

particle_loglikelihood 的输入包括死亡数据、候选参数、观察终点、粒子数、积分点、种子、重采样阈值和 soft/exact 配置。

输出是：

\[
\log \widehat p_\theta(Y_{0:T}^d).
\]

它是随机的 Monte Carlo 近似，不是解析精确值。

### 第 483–485 行

若参数无效，直接返回 \(-\infty\)。对优化器来说，这表示该参数不可能成为最优解。

### 第 487–492 行：生成面积积分点

若调用者没有提供 area_points：

1. 用固定 AREA_SEED 新建随机数生成器；
2. 分别均匀抽 M 个 x 和 M 个 y；
3. np.column_stack 把它们拼成形状 \((M,2)\) 的数组。

固定这些点属于 common random numbers 思路：比较不同参数时不让积分网格随意变化。

### 第 494–499 行：规范死亡数组

- 若没有死亡，构造形状 \((0,3)\) 的空数组，而不是形状 \((0,)\)；
- 否则先确保 deaths 是 float 数组；
- argsort(death_events[:,2]) 返回按时间列排序的行索引；
- 再按这些索引重排。

因此后面总按死亡时间从早到晚处理。

### 第 501–504 行：初始化粒子和权重

- rng：本次粒子滤波的随机数流；
- states：n_particles 个空状态；
- logw：每个粒子初始对数权重

\[
\log(1/N)=-\log N;
\]

- loglik=0：累计对数似然初值。

注意列表推导式每次都调用 ParticleState，所以每个粒子有不同的空列表。

### 第 506 行

t_prev=0：第一个传播区间从观察起点 0 开始。

### 第 509 行：遍历观测死亡

每一行死亡数据拆成：

- x_d：死亡 x 坐标；
- y_d：死亡 y 坐标；
- s_d：死亡时刻。

enumerate(...,start=1) 让显示编号 k 从 1 开始。

### 第 510–511 行

理论上数据已经排序；这里再次防御性检查，若当前时间小于上次时间就报错。

### 第 513 行

预分配长度 N 的 logG，用来存每个粒子在当前观测区间的增量对数权重。

### 第 515–516 行：逐粒子传播

对第 i 个粒子：

1. 从 t_prev 传播隐藏状态到 s_d；
2. 得到该区间无死亡的对数生存项 val。

函数会原地把 st 更新成死亡前一刻 \(Z_{s_d-}^{(i)}\)。

### 第 518–520 行：死亡事件强度项

在死亡触发新的 ERK 之前，用预跳状态计算：

\[
\lambda_i
=\lambda_\theta^d(x_d,y_d,s_d\mid Z_{s_d-}^{(i)}).
\]

随后：

\[
\text{val}
\leftarrow
\text{val}+\log\lambda_i.
\]

于是：

\[
\log G_k^{(i)}
=-\int_{s_{k-1}}^{s_k}h_s^{(i)}ds
+\log\lambda_i.
\]

等价地：

\[
G_k^{(i)}
=\exp\left(-\int h_s^{(i)}ds\right)\lambda_i.
\]

### 第 522–525 行：死亡后的 ERK 更新

死亡位置和时间是共同观测，不需要每个粒子重新抽；但 ERK 半径是隐藏 mark，所以每个粒子分别抽：

\[
R_{E,k}^{(i)}\sim\operatorname{Exp}(\beta_{d,R}).
\]

然后把 \((x_d,y_d,R_{E,k}^{(i)})\) 加入该粒子的 st.erk。

顺序非常重要：先用 \(Z_{s-}\) 算死亡强度，再加入死亡触发的 ERK。

### 第 527 行

把第 i 个粒子的区间增量对数似然存进 logG[i]。

### 第 529 行：未归一化权重更新

    new_logw_unnorm = logw + logG

普通尺度上是：

\[
\widetilde w_k^{(i)}
=w_{k-1}^{(i)}G_k^{(i)}.
\]

取对数后乘法变加法：

\[
\log\widetilde w_k^{(i)}
=\log w_{k-1}^{(i)}+\log G_k^{(i)}.
\]

### 第 530 行：增量似然

\[
\widehat c_k
=\sum_i w_{k-1}^{(i)}G_k^{(i)}
=\sum_i\widetilde w_k^{(i)}.
\]

inc 是它的对数：

\[
\text{inc}=\log\widehat c_k.
\]

使用 logsumexp 保证数值稳定。

### 第 531–534 行：粒子坍塌检查

若 inc 不是有限数，说明所有粒子给该观测的质量都为 0 或出现数值错误：

- verbose=True 时打印死亡编号；
- 返回 \(-\infty\)。

### 第 536 行：累计对数似然

\[
\log\widehat L_k
=\log\widehat L_{k-1}+\log\widehat c_k.
\]

最终相当于：

\[
\widehat L
=\prod_k\widehat c_k.
\]

### 第 537 行：归一化对数权重

\[
\log w_k^{(i)}
=\log\widetilde w_k^{(i)}-\log\widehat c_k.
\]

因此普通权重和为 1。

### 第 539–540 行：ESS

先把对数权重指数化，然后算：

\[
N_{\mathrm{eff}}
=\frac{1}{\sum_i(w_k^{(i)})^2}.
\]

- 全部等权时 \(N_{\mathrm{eff}}=N\)；
- 一个粒子权重为 1 时 \(N_{\mathrm{eff}}=1\)。

### 第 541–544 行：自适应重采样

若 ESS 小于阈值：

1. systematic_resample 返回 N 个祖先索引；
2. 根据索引复制祖先状态；
3. clone_state 保证后代不共享可变列表；
4. 重采样后所有粒子恢复等权 \(1/N\)。

为什么重采样后不是保留旧权重？因为选择次数已经编码了旧权重；再保留会重复加权。

### 第 546 行

当前死亡已处理完，把 t_prev 更新成 s_d，准备下一个死亡区间。

### 第 548–558 行：最后无死亡区间

最后一次死亡后到 T_end 之间虽然没有事件，仍然包含信息。

对每个粒子传播到 T_end，只加入：

\[
-\int_{s_{n_d}}^{T_{\mathrm{end}}}h_s^{(i)}\,ds.
\]

然后像前面一样：

1. 与旧 logw 相加；
2. logsumexp 得到最后一个无事件区间的增量似然；
3. 若无效则返回负无穷；
4. 加进 loglik。

此处之后不再需要归一化权重或重采样，因为已经没有后续观测。

### 第 560 行

把 NumPy/数值标量显式转为普通 float 后返回。

## 11. 第 567–666 行：参数拟合

### 第 567–581 行：函数签名

fit_parameters 接收死亡数据、基准参数、待估参数名、终点以及粒子和优化配置。

返回：

1. best_params：完整 ModelParams；
2. best_loglik：最优候选对应的粒子对数似然目标。

### 第 582–587 行：固定积分点

文档说明在对数参数空间最大化粒子似然。

随后用 AREA_SEED 一次生成固定 area_points。优化中的所有参数候选共用这些点，避免“某参数碰巧抽到更有利的积分网格”。

### 第 589 行

bounds=log_bounds(keys)：把待估参数的原始范围转成对数范围。

### 第 591 行

eval_counter 是可变字典：

- n：目标函数被调用次数；
- best：目前最小目标值，初始为正无穷。

为什么用字典而不是普通整数？内部函数 objective 对外层普通局部变量赋值时需要 nonlocal；修改字典内容则不需要。

### 第 593 行：内部目标函数

优化器每提出一个 log_vec，就调用 objective。SciPy 的优化器做最小化，所以这个函数最终返回负平均对数似然。

### 第 594–595 行

- 记录本次评估开始时间；
- 评估编号加 1。

### 第 597–599 行

把 log_vec 还原成完整正参数对象。若参数违反顺序等约束，就返回巨大惩罚 1e100。

注意：这里提前返回，不会走到后面的打印。因此运行日志可能从 eval 0002 跳到 eval 0004；缺失编号通常是无效候选，不是没有执行。

### 第 601–616 行：重复粒子滤波

- total=0：累计对数似然；
- 循环 pf_replicates 次；
- 每次种子为 pf_seed+1009r，避免完全重复同一条粒子路径；
- 若某次返回非有限似然，给优化器 1e90 的巨大惩罚；
- 否则累加 ll。

1009 只是选取的整数间隔，没有特殊统计公式。

### 第 618 行：优化目标

\[
\text{obj}
=-\frac1R\sum_{r=1}^R\log\widehat L_r.
\]

负号把“最大化对数似然”改成“最小化 obj”。

一个细节：它平均的是对数似然估计，不是先平均似然再取对数；两者一般不相等。

### 第 619–623 行

若 obj 小于历史最佳值：

- 更新 best；
- 在日志末尾加 NEW BEST。

否则标记为空字符串。

### 第 624–630 行：打印一次评估

- elapsed：本次参数评估耗时；
- getattr(p,k)：按字符串参数名读取数值；
- join：把多个 key=value 拼成一行；
- f-string 中 04d 表示整数至少四位并补零；
- .4f 表示保留四位小数；
- .5g 表示五位有效数字；
- flush=True 要求立即刷新输出，长时间运行时可及时看到进度。

### 第 631 行

返回 obj 给优化器。

### 第 633–635 行

打印优化即将开始、估计哪些参数、采用哪种似然模式、粒子数和面积点数。

### 第 637–647 行：差分进化

differential_evolution 是随机种群全局最小化方法。

参数逐项解释：

- objective：要最小化的函数；
- bounds：每个对数参数的有限边界；
- maxiter：最大进化代数；
- popsize：种群大小乘子；
- polish=False：不使用 SciPy 内置的最终局部优化，因为代码在后面自己控制；
- seed=987654：让差分进化种群可复现；
- updating="immediate"：一代内部一发现更好解就立即更新当前最佳；
- workers=1：串行计算；
- disp=True：显示每代进度。

### 第 649–650 行

- result_de.x：差分进化找到的最佳对数参数向量；
- result_de.fun：对应的最小目标值；
- 转成 float 便于后续比较和返回。

### 第 652–663 行：可选 L-BFGS-B 精修

仅当 polish=True 执行：

1. 从差分进化的 best_x 出发；
2. 使用有边界的 L-BFGS-B；
3. 最多 30 次迭代；
4. ftol=1e-3 是目标函数相对停止容差；
5. 只有局部结果更好时才替换全局结果。

因为粒子目标有 Monte Carlo 噪声且 soft/exact 结构不一定平滑，L-BFGS-B 未必可靠，所以 tiny test 默认关闭。

### 第 665–666 行

把最优对数参数还原成完整参数对象，并返回：

\[
(\text{best\_params},-\text{best\_obj}).
\]

由于 best_obj 是负对数似然，返回时再取负号恢复对数似然。

## 12. 第 674–775 行：诊断函数

### 第 674–698 行：death_spatial_diagnostic

目标是比较死亡在 T-zone 内外的空间密度。

#### 第 676–678 行

若 deaths 没有元素，打印“没有死亡”并结束函数。

#### 第 680–682 行

- n_total：死亡总数；
- 第 681 行逐行拆出 \((x,y,t)\)，用 is_inside_T_zone 判断并求和；
- 下划线 _ 接住不需要使用的时间；
- bool 在求和时 True 视为 1、False 视为 0；
- int 把结果明确转为整数；
- n_out=n_total-n_T。

#### 第 684–688 行

- area_T：中间竖条面积加左臂面积；
- area_out：窗口总面积减 T-zone 面积；
- dens_T：T-zone 每单位面积死亡数；
- dens_out：外部每单位面积死亡数；
- ratio：两密度之比。

条件表达式避免除以 0：

- 面积为 0 时返回 NaN；
- 外部密度为 0 时比值返回正无穷。

这个 density 只是观察到的计数除以面积，没有再除观察时长；比值中相同观察时长会抵消。

#### 第 690–698 行

按格式打印死亡数、面积、密度和密度比；.4f 保留 4 位小数。

注意：这个函数只做描述性诊断，没有计算 binomial test 的 p 值。

### 第 701–738 行：pf_noise_diagnostic

目标是固定同一组参数，换不同随机种子重复粒子滤波，从而估计 Monte Carlo 噪声。

#### 第 701–711 行

输入死亡、参数、终点、粒子数、固定积分点、模式、sigma、重复次数和显示标签；返回所有重复对数似然组成的数组。

#### 第 713–728 行

- lls=[]：收集每次对数似然；
- start：总计时起点；
- 循环 repeats 次；
- 每次用 PF_SEED+10000+1009r；
- 把 ll 加进列表；
- np.asarray 转成浮点数组；
- elapsed 是总耗时。

#### 第 730–738 行

打印：

- 重复次数和设置；
- 样本均值；
- 样本标准差；
- 最小值和最大值；
- 耗时。

np.std(...,ddof=1) 使用分母 \(R-1\) 的样本标准差；只有一次重复时人为显示 0，避免自由度不足。

最后返回 arr，便于调用者继续分析。

### 第 741–775 行：likelihood_profile_lambda_c

目标是固定其他参数，只改变 lambda_a_c，看一维对数似然形状。

#### 第 741–749 行

函数只打印结果，不返回实质数值，所以返回类型为 None。

#### 第 750–751 行

在 0.005 到 0.5 间构造 PROFILE_GRID_SIZE 个对数等距点：

1. 先对两个端点取 log；
2. 在线性 log 空间用 linspace 等分；
3. 再 exp 回原尺度。

这比线性网格更适合跨数量级的正参数。

#### 第 752–756 行

打印表头；best_lc 初始为 None，best_ll 初始为负无穷。

#### 第 757–760 行

遍历网格值：

- replace 复制 true_params，只换 lambda_a_c；
- 若违反 lambda_a_c ≤ lambda_a_T 等约束，用 continue 跳过本次循环。

#### 第 761–770 行

对当前 p_test 调用粒子滤波。所有网格点使用相同种子和相同面积点，让剖面比较更稳定。

#### 第 771–775 行

打印当前网格值和对数似然；若更大则保存；最后打印剖面最优点。

潜在边界情况：如果所有点都无效，best_lc 仍为 None，最后用 .6g 格式化会报错。不过当前网格中有有效点，所以不会发生。

## 13. 第 781–788 行：参数比较表

### 第 781 行

print_param_table 接收真实参数、估计参数和要显示的参数名。

### 第 782–784 行

打印标题和列名。

格式说明：

- <14：左对齐，宽度 14；
- >12：右对齐，宽度 12；
- >16：右对齐，宽度 16。

### 第 785–788 行

对每个 key：

1. getattr 读取真实值 tv；
2. getattr 读取估计值 ev；
3. 打印二者和比值 ev/tv。

例如比值 0.8 表示估计值是真值的 80%。

## 14. 第 791–947 行：main 主程序

### 第 791–801 行：定义真实参数

main 是整个实验入口。

true_params 创建一组完整的模拟真值：

\[
(5,\;0.5,\;0.05,\;1,\;2.5,\;1.2,\;2,\;0.8).
\]

这些值随后既用于制造假数据，也作为未估参数的固定值。

### 第 803–809 行：模拟死亡

先打印提示，再调用 simulate_death_events：

- 参数为 true_params；
- 最大时间 T_MAX=5；
- 目标死亡数 TARGET_DEATHS=8；
- 随机种子 123。

返回字典保存在 sim。

### 第 810–811 行

- deaths 取死亡事件数组；
- sim["final_time"] 是长度 1 的数组，先取第 0 个元素，再转为 float。

### 第 813–815 行

若一个死亡也没模拟出来：

1. 打印建议；
2. return 提前结束 main。

### 第 817–823 行：保存 CSV

np.savetxt 把 deaths 写到当前工作目录：

    simulated_death_events.csv

参数含义：

- delimiter=","：逗号分隔；
- header="x,y,t"：首行列名；
- comments=""：不要在表头前自动加 #。

程序从哪个目录启动，CSV 就写到哪个目录，不一定写在 Python 文件所在目录。

### 第 825–830 行：确定观察终点

- 若固定时间观察，即 TARGET_DEATHS=None，则 T_end=T_MAX；
- 否则是在达到目标死亡数时停止，T_end=模拟停止时刻 final_time。

这是统计上很重要的区别。固定时间窗的普通点过程似然解释更直接；按第 8 次死亡停止属于随机停止设计。

### 第 832–835 行

打印死亡数、模拟器最后时间、似然观察终点和 CSV 文件名。

### 第 837–838 行

若空间诊断开关为 True，就调用 death_spatial_diagnostic。

### 第 840–845 行：诊断积分点

再用 AREA_SEED 构造固定的 \((M,2)\) 积分点 diagnostic_area_points。

因为 fit_parameters 也使用相同 AREA_SEED 和相同 M，它们通常是同一组坐标；这使之后真值与估计值的似然比较使用共同面积近似。

### 第 847–858 行：优化前 PF 噪声诊断

只有 RUN_PF_NOISE_DIAGNOSTIC=True 时才执行。

它在真参数处重复计算粒子对数似然，报告优化前的 Monte Carlo 波动。

函数调用采用关键字参数，所以顺序清楚，而且不易把多个 float 参数传错位置。

### 第 860–869 行：似然剖面

只有 RUN_LIKELIHOOD_PROFILE=True 时执行，扫描 lambda_a_c。

### 第 871–873 行：基准参数

    base_params = true_params

这表示当前仿真实验里，未估计的参数直接固定在真值。

真实数据中你不知道真值，所以注释提醒要换成事先选择的固定值、外部估计值或初始值。

### 第 875–889 行：正式优化

调用 fit_parameters，估计 ESTIMATE_KEYS 中的两个参数。

多返回值解包：

- estimated_params：完整估计参数对象；
- best_loglik：优化内部最佳目标对应的粒子对数似然。

其余参数逐项从全局配置传入。

### 第 890–899 行：在真参数处重新算诊断似然

使用：

- 同一 death 数据；
- true_params；
- diagnostic_area_points；
- 种子 PF_SEED+999。

它与优化内部用的种子不同，所以 ll_true 是独立一些的诊断性重新评估。

### 第 901–910 行：在估计参数处重新算诊断似然

设置与上一段完全一样，只把参数换成 estimated_params。

两者使用同一随机种子和同一面积点，这是一种配对比较：随机环境尽量相同，差异更主要来自参数。

### 第 912–916 行：比较真值和估计值

打印：

- 真参数处对数似然；
- 估计参数处对数似然；
- 二者之差。

若差值为正，说明在这一次配对粒子评估中，估计参数比真参数拟合得更好。

这不奇怪：有限样本的 MLE 不必等于生成真值；粒子 Monte Carlo 噪声也会造成差异。

### 第 918–929 行：优化后 PF 噪声诊断

若开关打开，在 estimated_params 处重复计算对数似然，便于判断“估计优于真值的差距”是否大于 PF 自身噪声。

### 第 931–935 行

- 打印待估参数的真值、估计值和比值；
- 打印优化内部 best_loglik；
- 打印完整 ModelParams，包括没有估计、保持固定的参数。

注意 best_loglik 可能不同于上面的 ll_est，因为它们使用不同 PF 种子。

### 第 937–943 行：最终提示

程序提醒：

1. PF 标准差若和真值/估计值似然差同量级，就应增加粒子数和重复数；
2. 固定时间窗更适合清楚的点过程似然；
3. 可逐渐减小 SOFT_SIGMA，再尝试 exact；
4. 仅靠死亡数据可能无法同时识别所有 caspase 和 ERK 参数，应从小参数子集开始。

### 第 946–947 行：真正的程序入口

Python 直接运行此文件时，内置变量 __name__ 等于 "__main__"，于是调用 main。

若另一个 Python 文件只是：

    import pf_mle_caspase_erk_TINY_TEST

那么 __name__ 是模块名，不会自动运行 main。这样可以安全复用里面的函数。

## 15. 三条最核心数学公式与代码对应

### 15.1 点过程似然

对于给定隐藏路径的死亡点过程：

\[
L(Y\mid Z)
=
\exp\left(
-\int_0^T\lambda_d
|A(V_s^a)\setminus A(V_s^p)|\,ds
\right)
\prod_{k=1}^{n_d}
\lambda_\theta^d(x_k,y_k,s_k\mid Z_{s_k-}).
\]

代码对应：

- propagate_hidden_until：负积分；
- death_event_intensity：每个事件强度；
- 第 520 行：对数域相加。

### 15.2 粒子权重

\[
\widetilde w_k^{(i)}
=w_{k-1}^{(i)}G_k^{(i)},\qquad
w_k^{(i)}
=\frac{\widetilde w_k^{(i)}}
{\sum_j\widetilde w_k^{(j)}}.
\]

代码对应：

- 第 529 行：未归一化；
- 第 530 行：归一化常数的对数；
- 第 537 行：归一化。

### 15.3 粒子似然

\[
\widehat L
=\prod_k
\left[
\sum_iw_{k-1}^{(i)}G_k^{(i)}
\right].
\]

取对数：

\[
\log\widehat L
=\sum_k
\log\left[
\sum_iw_{k-1}^{(i)}G_k^{(i)}
\right].
\]

代码对应第 530、536 和 558 行。

## 16. 这份 tiny-test 代码中需要特别小心的地方

### 16.1 20 个粒子、50 个面积点、2 代优化只适合检查能否运行

它们不足以支持稳定的正式结论。正式推断至少要查看 PF 噪声随 N 增大是否下降、优化结果是否在多个种子下稳定。

### 16.2 soft 不是原始硬模型

soft 模式把圆盘边界改成 sigmoid，能减少权重坍塌，但估计的是近似模型。SOFT_SIGMA 越小越接近硬边界，同时通常也越难算。

### 16.3 exact 模式仍把 0 替换成 1e-12

因此逻辑上不可能的粒子不会得到真正零权重，而是极小权重。若要数学上完全 exact，应专门在对数域允许 \(-\infty\)，并处理全体坍塌。

### 16.4 粒子重复数大于 1 时，代码平均 log-likelihood

当前目标是：

\[
-\frac1R\sum_r\log\widehat L_r.
\]

它不等于：

\[
-\log\left(\frac1R\sum_r\widehat L_r\right).
\]

这是实用的降噪选择，但解释结果时要知道二者不同。

### 16.5 固定第 8 次死亡停止与固定观察时间不是同一抽样设计

程序自己也推荐固定时间窗。若正式论文以第 n 次死亡作为停止规则，应明确写出你是在条件于 n、条件于停止时间，还是使用相应停止时刻似然。

### 16.6 只观察 8 次死亡不可能可靠识别很多参数

当前只估两个参数都可能很不稳定，更不能把所有八个参数一次放进去就期待得到可信真值恢复。

### 16.7 有两个定义没有在当前主流程使用

- Iterable 导入后未使用；
- pack_log_params 定义后未调用。

它们不导致错误，只是可以清理。

## 17. 一次运行时各主要对象的形状

| 对象 | 典型形状/类型 | 含义 |
| --- | --- | --- |
| deaths | \((8,3)\) 数组 | 每行为 x、y、t |
| area_points | \((50,2)\) 数组 | 固定空间积分点 |
| states | 长度 20 的列表 | 20 个 ParticleState |
| st.active | 可变长度列表 | 当前激活圆盘 |
| st.erk | 可变长度列表 | 当前保护圆盘 |
| logw | \((20,)\) 数组 | 归一化对数权重 |
| logG | \((20,)\) 数组 | 当前区间增量对数似然 |
| ancestors | \((20,)\) 整数数组 | 重采样祖先索引 |
| log_vec | \((2,)\) 数组 | 两个待估参数的对数 |

## 18. 官方文档与数学参考

- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)：解释 @dataclass、frozen=True 和 replace。
- [NumPy Generator.exponential](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.exponential.html)：明确参数是 scale，即率的倒数。
- [SciPy differential_evolution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html)：解释 maxiter、popsize、updating、workers 和返回对象。
- [Doucet 与 Johansen 的粒子滤波教程](https://web-static-aws.seas.harvard.edu/courses/cs281/papers/doucet-johansen.pdf)：解释 bootstrap particle filter、ESS 阈值与系统重采样。
- [Soen 等人的点过程论文](https://ojs.aaai.org/index.php/AAAI/article/view/17165/16972)：第 2 节写出了“事件强度乘积 × 负积分指数”的点过程似然形式。

## 19. 最短复习版

如果你现在只记住五件事：

1. 模拟器已知参数生成死亡；粒子滤波拿死亡反推参数。
2. 每个粒子是一条可能的隐藏 active/ERK 历史。
3. 无死亡区间贡献 \(-\int\lambda\)，死亡时刻贡献 \(+\log\lambda\)。
4. 新权重等于旧权重乘当前区间似然；对数域中就是相加。
5. 外层优化器最小化负对数似然，因此找到的就是近似 MLE。
