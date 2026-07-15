"""
Particle-filter maximum likelihood for an observation-driven caspase--ERK
point-process model.

This script is written to match the user's Gillespie simulator structure:
    hidden caspase activation V^a_t;
    observed death events Y^d = {(y_i^d, s_i^d)};
    ERK protection V^p_t triggered after observed deaths.

Key modelling correction:
    The particle filter does NOT treat X_t=(V^a_t,V^p_t) as an autonomous HMM.
    The rigorous augmented state is
        Z_t = (V^a_t, V^p_t, V^d_{0:t}),
    where V^d_{0:t} is the observed death history. In code, V^d is common to
    all particles, so each particle stores only (V^a_t,V^p_t), while transitions
    and likelihood are computed conditionally on the observed death history.

What the script does:
    1. Simulate synthetic death-event data from the original Gillespie model.
    2. Estimate selected parameters by maximizing a particle-filter likelihood.

Important practical warning:
    With the exact hard indicator death intensity,
        lambda_d * 1{x in A(Va)} * 1{x not in A(Vp)},
    a bootstrap particle filter can suffer severe weight collapse because a
    randomly simulated hidden activation field often does not cover the exact
    observed death location. For debugging/inference, this script includes
    LIKELIHOOD_MODE = "soft", a smooth approximation to the hard indicator.
    Set LIKELIHOOD_MODE = "exact" when you want the literal model.

Dependencies:
    numpy, scipy

Run:
    python pf_mle_caspase_erk_observation_driven.py
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Iterable, List, Sequence, Tuple
import math
import time
import numpy as np

try:
    from scipy.optimize import differential_evolution, minimize
except Exception as exc:  # pragma: no cover
    raise ImportError("This script needs scipy: pip install scipy") from exc


# ============================================================
# 1. Global configuration for a first runnable demo
# ============================================================

# Spatial domain W = [0,Lx] x [0,Ly]
Lx = 10.0
Ly = 10.0
AREA_W = Lx * Ly

# Fixed T-zone definition, copied from the uploaded simulator.
x1 = Lx / 3.0
x2 = 2.0 * Lx / 3.0
y1 = Ly / 3.0
y2 = 2.0 * Ly / 3.0

# Recommended simulation mode for likelihood inference:
#   fixed-time window is cleaner than stopping exactly at the 60th death.
#   If this is too slow, set USE_FIXED_TIME_WINDOW=False.
USE_FIXED_TIME_WINDOW = True
T_MAX = 2.0
TARGET_DEATHS = None if USE_FIXED_TIME_WINDOW else 8

# Particle filter settings.
# Start here; increase N_PARTICLES / PF_REPLICATES for final results.
N_PARTICLES = 30
AREA_MC_POINTS = 100
RESAMPLE_THRESHOLD = 0.75  # Alg. 7 in the notes uses N_eff / N <= 0.75
RESAMPLE_METHOD = "residual_systematic"  # multinomial, systematic, stratified, residual_multinomial, residual_systematic
PF_REPLICATES = 3
PF_SEED = 20260709
AREA_SEED = 20260710

# "exact" uses hard indicators. "soft" uses a smooth approximation.
# A smaller SOFT_SIGMA is closer to the exact model but can be noisier.
LIKELIHOOD_MODE = "soft"  # "soft" or "exact"
SOFT_SIGMA = 0.10
MIN_EVENT_INTENSITY = 1e-12

# Optimization settings. Increase maxiter/popsize for better inference.
OPT_MAXITER = 3
OPT_POPSIZE = 4
POLISH_WITH_LBFGSB = False

# Diagnostics. They cost extra time but are very useful for debugging inference.
RUN_DEATH_SPATIAL_DIAGNOSTIC = True
RUN_PF_NOISE_DIAGNOSTIC = True
PF_NOISE_REPEATS = 5
RUN_LIKELIHOOD_PROFILE = False
PROFILE_GRID_SIZE = 15

# Estimate a subset first. Do not estimate all parameters at once at the beginning.
# Start with identifiable parameters. Do NOT estimate all five at first.
# After this works, try adding "lambda_d", then radius/lifetime parameters one by one.
ESTIMATE_KEYS = (
    "lambda_a_T",
    "lambda_a_c",
)

# ============================================================
# 2. Parameters and state
# ============================================================

@dataclass(frozen=True)
class ModelParams:
    # Caspase activation intensities
    lambda_a_1: float = 5.00   # dominating intensity and active-zone intensity
    lambda_a_T: float = 0.50   # background activation intensity inside T-zone
    lambda_a_c: float = 0.05   # background activation intensity outside T-zone

    # Death intensity on active and unprotected region
    lambda_d: float = 1.00

    # Activation mark/lifetime parameters
    beta_a_R: float = 2.50     # R^a ~ Exp(beta_a_R)
    beta_a_T: float = 1.20     # active-center expiration rate

    # ERK mark/lifetime parameters
    beta_d_R: float = 2.00     # R^d ~ Exp(beta_d_R)
    beta_d_T: float = 0.80     # ERK-zone expiration rate


@dataclass
class ParticleState:
    # Each list contains tuples (x,y,r)
    active: List[Tuple[float, float, float]]
    erk: List[Tuple[float, float, float]]


def clone_state(st: ParticleState) -> ParticleState:
    return ParticleState(active=list(st.active), erk=list(st.erk))


def valid_params(p: ModelParams) -> bool:
    vals = [
        p.lambda_a_1, p.lambda_a_T, p.lambda_a_c, p.lambda_d,
        p.beta_a_R, p.beta_a_T, p.beta_d_R, p.beta_d_T,
    ]
    if not all(np.isfinite(vals)) or not all(v > 0 for v in vals):
        return False
    return p.lambda_a_c <= p.lambda_a_T <= p.lambda_a_1


# Bounds for direct positive parameters. Optimizer works in log-space.
PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {
    "lambda_a_1": (0.2, 12.0),
    # Background intensities. Bounds are intentionally moderate for stable first runs.
    "lambda_a_T": (0.02, 2.0),
    "lambda_a_c": (0.002, 0.8),
    "lambda_d": (0.05, 5.0),
    "beta_a_R": (0.2, 8.0),
    "beta_a_T": (0.05, 5.0),
    "beta_d_R": (0.2, 8.0),
    "beta_d_T": (0.05, 5.0),
}


def unpack_log_params(log_vec: Sequence[float], base: ModelParams, keys: Sequence[str]) -> ModelParams:
    p = base
    for key, log_value in zip(keys, log_vec):
        p = replace(p, **{key: float(np.exp(log_value))})
    return p


def pack_log_params(p: ModelParams, keys: Sequence[str]) -> np.ndarray:
    return np.array([math.log(getattr(p, key)) for key in keys], dtype=float)


def log_bounds(keys: Sequence[str]) -> List[Tuple[float, float]]:
    return [(math.log(PARAM_BOUNDS[k][0]), math.log(PARAM_BOUNDS[k][1])) for k in keys]


# ============================================================
# 3. Geometry helpers
# ============================================================

def is_inside_T_zone(x: float, y: float) -> bool:
    inside_middle_column = (x1 <= x <= x2) and (0.0 <= y <= Ly)
    inside_left_arm = (0.0 <= x <= x1) and (y1 <= y <= y2)
    return inside_middle_column or inside_left_arm


def inside_union_exact(x: float, y: float, discs: Sequence[Tuple[float, float, float]]) -> bool:
    for cx, cy, r in discs:
        if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
            return True
    return False


def local_activation_intensity(x: float, y: float, st: ParticleState, p: ModelParams) -> float:
    if inside_union_exact(x, y, st.active):
        return p.lambda_a_1
    if is_inside_T_zone(x, y):
        return p.lambda_a_T
    return p.lambda_a_c


def _sigmoid_clipped(z: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50.0, 50.0)))


def soft_union_probability_points(
    points: np.ndarray,
    discs: Sequence[Tuple[float, float, float]],
    sigma: float,
) -> np.ndarray:
    """
    Smooth approximation of 1{x in union of discs}.
    For one disc, use sigmoid((r - distance)/sigma).
    For a union, use the max boundary score over discs.
    """
    n = points.shape[0]
    if len(discs) == 0:
        return np.zeros(n, dtype=float)
    scores = np.full(n, -1e9, dtype=float)
    px = points[:, 0]
    py = points[:, 1]
    for cx, cy, r in discs:
        dist = np.sqrt((px - cx) ** 2 + (py - cy) ** 2)
        scores = np.maximum(scores, r - dist)
    return _sigmoid_clipped(scores / sigma)


def soft_union_probability_one(
    x: float,
    y: float,
    discs: Sequence[Tuple[float, float, float]],
    sigma: float,
) -> float:
    if len(discs) == 0:
        return 0.0
    best = -1e9
    for cx, cy, r in discs:
        dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        best = max(best, r - dist)
    return float(_sigmoid_clipped(best / sigma))


def active_unprotected_area(
    st: ParticleState,
    area_points: np.ndarray,
    mode: str = "exact",
    sigma: float = SOFT_SIGMA,
) -> float:
    r"""Approximate |A(Va) \ A(Vp)| by fixed Monte Carlo quadrature points."""
    if len(st.active) == 0:
        return 0.0

    if mode == "exact":
        active = np.zeros(area_points.shape[0], dtype=bool)
        protected = np.zeros(area_points.shape[0], dtype=bool)
        px = area_points[:, 0]
        py = area_points[:, 1]
        for cx, cy, r in st.active:
            active |= (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2
        for cx, cy, r in st.erk:
            protected |= (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2
        return AREA_W * float(np.mean(active & (~protected)))

    if mode == "soft":
        p_active = soft_union_probability_points(area_points, st.active, sigma)
        p_protected = soft_union_probability_points(area_points, st.erk, sigma)
        return AREA_W * float(np.mean(p_active * (1.0 - p_protected)))

    raise ValueError(f"Unknown likelihood mode: {mode}")


def death_event_intensity(
    x: float,
    y: float,
    st: ParticleState,
    p: ModelParams,
    mode: str = "exact",
    sigma: float = SOFT_SIGMA,
    min_intensity: float = MIN_EVENT_INTENSITY,
) -> float:
    """lambda^d_theta(y,s | Z_{s-}) before the observed death triggers ERK."""
    if mode == "exact":
        ok = inside_union_exact(x, y, st.active) and (not inside_union_exact(x, y, st.erk))
        return p.lambda_d if ok else min_intensity

    if mode == "soft":
        pa = soft_union_probability_one(x, y, st.active, sigma)
        pp = soft_union_probability_one(x, y, st.erk, sigma)
        return max(min_intensity, p.lambda_d * pa * (1.0 - pp))

    raise ValueError(f"Unknown likelihood mode: {mode}")


# ============================================================
# 4. Synthetic simulator: exact Gillespie model, no plots
# ============================================================

def simulate_death_events(
    p: ModelParams,
    T_max: float = T_MAX,
    target_deaths: int | None = TARGET_DEATHS,
    seed: int = 123,
) -> Dict[str, np.ndarray]:
    """Simulate the original model and return death events plus hidden histories."""
    if not valid_params(p):
        raise ValueError("Invalid parameters for simulation.")

    rng = np.random.default_rng(seed)
    st = ParticleState(active=[], erk=[])
    t = 0.0

    cas_events: List[Tuple[float, float, float]] = []
    death_events: List[Tuple[float, float, float]] = []

    while t < T_max and (target_deaths is None or len(death_events) < target_deaths):
        n_active = len(st.active)
        n_erk = len(st.erk)

        activation_proposal_rate = p.lambda_a_1 * AREA_W
        death_proposal_rate = p.lambda_d * AREA_W
        active_expiration_rate = n_active * p.beta_a_T
        erk_expiration_rate = n_erk * p.beta_d_T

        a0 = activation_proposal_rate + death_proposal_rate + active_expiration_rate + erk_expiration_rate
        if a0 <= 0.0:
            break

        t += rng.exponential(1.0 / a0)
        if t > T_max:
            break

        u = rng.uniform()
        pa = activation_proposal_rate / a0
        pd = death_proposal_rate / a0
        pe = active_expiration_rate / a0

        if u <= pa:
            # Candidate activation, thinned by local activation intensity.
            x = rng.uniform(0.0, Lx)
            y = rng.uniform(0.0, Ly)
            lam = local_activation_intensity(x, y, st, p)
            if rng.uniform() <= lam / p.lambda_a_1:
                r = rng.exponential(1.0 / p.beta_a_R)
                st.active.append((x, y, r))
                cas_events.append((x, y, t))

        elif u <= pa + pd:
            # Candidate death, accepted iff active and unprotected.
            x = rng.uniform(0.0, Lx)
            y = rng.uniform(0.0, Ly)
            if inside_union_exact(x, y, st.active) and (not inside_union_exact(x, y, st.erk)):
                death_events.append((x, y, t))
                rE = rng.exponential(1.0 / p.beta_d_R)
                st.erk.append((x, y, rE))

        elif u <= pa + pd + pe:
            # Active expiration.
            if st.active:
                idx = rng.integers(0, len(st.active))
                st.active.pop(int(idx))

        else:
            # ERK expiration.
            if st.erk:
                idx = rng.integers(0, len(st.erk))
                st.erk.pop(int(idx))

    return {
        "death_events": np.array(death_events, dtype=float),  # columns: x,y,t
        "cas_events": np.array(cas_events, dtype=float),
        "final_time": np.array([t], dtype=float),
    }


# ============================================================
# 5. Particle filter likelihood conditional on observed deaths
# ============================================================

def propagate_hidden_until(
    st: ParticleState,
    t0: float,
    t1: float,
    p: ModelParams,
    rng: np.random.Generator,
    area_points: np.ndarray,
    mode: str,
    sigma: float,
) -> float:
    """
    Propagate only the hidden mechanisms between observed death times:
      - activation proposals/accepted activations;
      - active expirations;
      - ERK expirations.

    Deaths are not simulated here because they are observed. Their likelihood
    contribution is accumulated as exp(-integral lambda) between events and
    lambda(y,s | Z_{s-}) at each observed death.

    Returns log survival factor: -int_{t0}^{t1} lambda_d |A(Va)\\A(Vp)| dt.
    """
    t = t0
    log_survival = 0.0

    while t < t1:
        n_active = len(st.active)
        n_erk = len(st.erk)

        activation_proposal_rate = p.lambda_a_1 * AREA_W
        active_expiration_rate = n_active * p.beta_a_T
        erk_expiration_rate = n_erk * p.beta_d_T
        a0_hidden = activation_proposal_rate + active_expiration_rate + erk_expiration_rate

        # Current observed-death hazard under this particle.
        death_area = active_unprotected_area(st, area_points, mode=mode, sigma=sigma)
        death_hazard = p.lambda_d * death_area

        if a0_hidden <= 0.0:
            log_survival -= death_hazard * (t1 - t)
            break

        dt = rng.exponential(1.0 / a0_hidden)
        if t + dt >= t1:
            log_survival -= death_hazard * (t1 - t)
            t = t1
            break

        log_survival -= death_hazard * dt
        t += dt

        u = rng.uniform()
        pa = activation_proposal_rate / a0_hidden
        pe = active_expiration_rate / a0_hidden

        if u <= pa:
            x = rng.uniform(0.0, Lx)
            y = rng.uniform(0.0, Ly)
            lam = local_activation_intensity(x, y, st, p)
            if rng.uniform() <= lam / p.lambda_a_1:
                r = rng.exponential(1.0 / p.beta_a_R)
                st.active.append((x, y, r))

        elif u <= pa + pe:
            if st.active:
                idx = rng.integers(0, len(st.active))
                st.active.pop(int(idx))

        else:
            if st.erk:
                idx = rng.integers(0, len(st.erk))
                st.erk.pop(int(idx))

    return log_survival


def logsumexp_np(a: np.ndarray) -> float:
    m = float(np.max(a))
    if not np.isfinite(m):
        return -np.inf
    return m + math.log(float(np.sum(np.exp(a - m))))


def _normalize_weights_safe(weights: np.ndarray) -> np.ndarray:
    """Numerically safe normalization for already nonnegative weights."""
    weights = np.asarray(weights, dtype=float)
    total = float(np.sum(weights))
    if (not np.isfinite(total)) or total <= 0.0:
        raise ValueError("Cannot resample: weights are not normalizable.")
    weights = weights / total
    # Make the last cumulative value exactly 1.0 after cumsum.
    weights[-1] = max(0.0, 1.0 - float(np.sum(weights[:-1])))
    return weights


def multinomial_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Basic multinomial redistribution: N iid draws from the discrete weights."""
    weights = _normalize_weights_safe(weights)
    n = len(weights)
    return rng.choice(n, size=n, replace=True, p=weights)


def systematic_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Kitagawa/systematic redistribution: u_1~U(0,1/N), u_i=u_1+(i-1)/N."""
    weights = _normalize_weights_safe(weights)
    n = len(weights)
    positions = (rng.uniform() + np.arange(n)) / n
    cumsum = np.cumsum(weights)
    cumsum[-1] = 1.0
    return np.searchsorted(cumsum, positions, side="right")


def stratified_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Stratified redistribution: one uniform draw in each interval [i/N,(i+1)/N)."""
    weights = _normalize_weights_safe(weights)
    n = len(weights)
    positions = (np.arange(n) + rng.uniform(size=n)) / n
    cumsum = np.cumsum(weights)
    cumsum[-1] = 1.0
    return np.searchsorted(cumsum, positions, side="right")


def residual_multinomial_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Residual redistribution: deterministic floor(Nw_i) copies, multinomial for residues."""
    weights = _normalize_weights_safe(weights)
    n = len(weights)
    counts = np.floor(n * weights).astype(int)
    ancestors = [i for i, c in enumerate(counts) for _ in range(int(c))]
    r = n - len(ancestors)
    if r > 0:
        residual = n * weights - counts
        residual_sum = float(np.sum(residual))
        if residual_sum <= 0.0:
            extra = rng.integers(0, n, size=r)
        else:
            residual = residual / residual_sum
            residual[-1] = max(0.0, 1.0 - float(np.sum(residual[:-1])))
            extra = rng.choice(n, size=r, replace=True, p=residual)
        ancestors.extend(map(int, extra))
    ancestors = np.asarray(ancestors, dtype=int)
    rng.shuffle(ancestors)
    return ancestors


def residual_systematic_resample(weights: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Residual + Kitagawa: deterministic floor(Nw_i) copies, systematic for residues."""
    weights = _normalize_weights_safe(weights)
    n = len(weights)
    counts = np.floor(n * weights).astype(int)
    ancestors = [i for i, c in enumerate(counts) for _ in range(int(c))]
    r = n - len(ancestors)
    if r > 0:
        residual = n * weights - counts
        residual_sum = float(np.sum(residual))
        if residual_sum <= 0.0:
            extra = rng.integers(0, n, size=r)
        else:
            residual = residual / residual_sum
            residual[-1] = max(0.0, 1.0 - float(np.sum(residual[:-1])))
            positions = (rng.uniform() + np.arange(r)) / r
            cumsum = np.cumsum(residual)
            cumsum[-1] = 1.0
            extra = np.searchsorted(cumsum, positions, side="right")
        ancestors.extend(map(int, extra))
    ancestors = np.asarray(ancestors, dtype=int)
    rng.shuffle(ancestors)
    return ancestors


def resample_indices(weights: np.ndarray, rng: np.random.Generator, method: str = RESAMPLE_METHOD) -> np.ndarray:
    """Choose the redistribution scheme used by the particle filter."""
    if method == "multinomial":
        return multinomial_resample(weights, rng)
    if method == "systematic":
        return systematic_resample(weights, rng)
    if method == "stratified":
        return stratified_resample(weights, rng)
    if method == "residual_multinomial":
        return residual_multinomial_resample(weights, rng)
    if method == "residual_systematic":
        return residual_systematic_resample(weights, rng)
    raise ValueError(f"Unknown RESAMPLE_METHOD={method!r}")


def particle_loglikelihood(
    death_events: np.ndarray,
    p: ModelParams,
    T_end: float,
    n_particles: int = N_PARTICLES,
    area_points: np.ndarray | None = None,
    seed: int = PF_SEED,
    resample_threshold: float = RESAMPLE_THRESHOLD,
    resample_method: str = RESAMPLE_METHOD,
    mode: str = LIKELIHOOD_MODE,
    sigma: float = SOFT_SIGMA,
    verbose: bool = False,
) -> float:
    """Bootstrap particle estimate of log p_theta(Y^d_{0:T})."""
    if not valid_params(p):
        return -np.inf

    if area_points is None:
        rng_area = np.random.default_rng(AREA_SEED)
        area_points = np.column_stack([
            rng_area.uniform(0.0, Lx, AREA_MC_POINTS),
            rng_area.uniform(0.0, Ly, AREA_MC_POINTS),
        ])

    if death_events.size == 0:
        death_events = np.empty((0, 3), dtype=float)
    else:
        death_events = np.asarray(death_events, dtype=float)
        order = np.argsort(death_events[:, 2])
        death_events = death_events[order]

    rng = np.random.default_rng(seed)
    states = [ParticleState(active=[], erk=[]) for _ in range(n_particles)]
    logw = np.full(n_particles, -math.log(n_particles), dtype=float)
    loglik = 0.0

    t_prev = 0.0

    # Process observed deaths in chronological order.
    for k, (x_d, y_d, s_d) in enumerate(death_events, start=1):
        if s_d < t_prev:
            raise ValueError("Death events must be sorted by increasing time.")

        logG = np.empty(n_particles, dtype=float)

        for i, st in enumerate(states):
            val = propagate_hidden_until(st, t_prev, float(s_d), p, rng, area_points, mode, sigma)

            # Use pre-jump state Z_{s-} for the likelihood contribution.
            lam_event = death_event_intensity(float(x_d), float(y_d), st, p, mode=mode, sigma=sigma)
            val += math.log(lam_event)

            # After observing the death, update common death history implicitly,
            # and sample the hidden ERK protection mark for this particle.
            rE = rng.exponential(1.0 / p.beta_d_R)
            st.erk.append((float(x_d), float(y_d), rE))

            logG[i] = val

        new_logw_unnorm = logw + logG
        inc = logsumexp_np(new_logw_unnorm)
        if not np.isfinite(inc):
            if verbose:
                print(f"All particles collapsed at observed death {k}.")
            return -np.inf

        loglik += inc
        logw = new_logw_unnorm - inc

        weights = np.exp(logw)
        neff = 1.0 / float(np.sum(weights ** 2))
        if neff / n_particles <= resample_threshold:
            ancestors = resample_indices(weights, rng, method=resample_method)
            states = [clone_state(states[int(j)]) for j in ancestors]
            logw.fill(-math.log(n_particles))

        t_prev = float(s_d)

    # Final no-death interval [last death, T_end].
    if T_end > t_prev:
        logG = np.empty(n_particles, dtype=float)
        for i, st in enumerate(states):
            logG[i] = propagate_hidden_until(st, t_prev, T_end, p, rng, area_points, mode, sigma)

        new_logw_unnorm = logw + logG
        inc = logsumexp_np(new_logw_unnorm)
        if not np.isfinite(inc):
            return -np.inf
        loglik += inc

    return float(loglik)


# ============================================================
# 6. Parameter fitting by particle maximum likelihood
# ============================================================

def fit_parameters(
    death_events: np.ndarray,
    base_params: ModelParams,
    keys: Sequence[str],
    T_end: float,
    n_particles: int = N_PARTICLES,
    area_mc_points: int = AREA_MC_POINTS,
    pf_seed: int = PF_SEED,
    pf_replicates: int = PF_REPLICATES,
    resample_method: str = RESAMPLE_METHOD,
    mode: str = LIKELIHOOD_MODE,
    sigma: float = SOFT_SIGMA,
    maxiter: int = OPT_MAXITER,
    popsize: int = OPT_POPSIZE,
    polish: bool = POLISH_WITH_LBFGSB,
) -> Tuple[ModelParams, float]:
    """Maximize the particle likelihood over selected log-parameters."""
    rng_area = np.random.default_rng(AREA_SEED)
    area_points = np.column_stack([
        rng_area.uniform(0.0, Lx, area_mc_points),
        rng_area.uniform(0.0, Ly, area_mc_points),
    ])

    bounds = log_bounds(keys)

    eval_counter = {"n": 0, "best": np.inf}

    def objective(log_vec: np.ndarray) -> float:
        t_start = time.time()
        eval_counter["n"] += 1

        p = unpack_log_params(log_vec, base_params, keys)
        if not valid_params(p):
            return 1e100

        total = 0.0
        for r in range(pf_replicates):
            ll = particle_loglikelihood(
                death_events=death_events,
                p=p,
                T_end=T_end,
                n_particles=n_particles,
                area_points=area_points,
                seed=pf_seed + 1009 * r,
                resample_method=resample_method,
                mode=mode,
                sigma=sigma,
                verbose=False,
            )
            if not np.isfinite(ll):
                return 1e90
            total += ll

        obj = -total / pf_replicates
        if obj < eval_counter["best"]:
            eval_counter["best"] = float(obj)
            best_mark = "  NEW BEST"
        else:
            best_mark = ""
        elapsed = time.time() - t_start
        vals = ", ".join(f"{k}={getattr(p, k):.5g}" for k in keys)
        print(
            f"eval {eval_counter['n']:04d}: obj={obj:.4f}, loglik={-obj:.4f}, "
            f"time={elapsed:.2f}s, {vals}{best_mark}",
            flush=True,
        )
        return obj

    print("\nStarting differential evolution optimization...")
    print(f"  estimating keys: {list(keys)}")
    print(f"  mode={mode}, particles={n_particles}, area points={area_mc_points}")
    print(f"  resampling={resample_method}, threshold={RESAMPLE_THRESHOLD}")

    result_de = differential_evolution(
        objective,
        bounds=bounds,
        maxiter=maxiter,
        popsize=popsize,
        polish=False,
        seed=987654,
        updating="immediate",
        workers=1,
        disp=True,
    )

    best_x = result_de.x
    best_obj = float(result_de.fun)

    if polish:
        print("\nPolishing with L-BFGS-B...")
        result_local = minimize(
            objective,
            best_x,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 30, "ftol": 1e-3},
        )
        if result_local.fun < best_obj:
            best_x = result_local.x
            best_obj = float(result_local.fun)

    best_params = unpack_log_params(best_x, base_params, keys)
    return best_params, -best_obj



# ============================================================
# 7. Diagnostics
# ============================================================

def death_spatial_diagnostic(deaths: np.ndarray) -> None:
    """Print whether deaths are enriched inside the fixed T-zone."""
    if deaths.size == 0:
        print("\nDeath spatial diagnostic: no deaths.")
        return

    n_total = len(deaths)
    n_T = int(sum(is_inside_T_zone(float(x), float(y)) for x, y, _ in deaths))
    n_out = n_total - n_T

    area_T = (x2 - x1) * Ly + x1 * (y2 - y1)
    area_out = AREA_W - area_T
    dens_T = n_T / area_T if area_T > 0 else float("nan")
    dens_out = n_out / area_out if area_out > 0 else float("nan")
    ratio = dens_T / dens_out if dens_out > 0 else float("inf")

    print("\nDeath spatial diagnostic")
    print("------------------------")
    print(f"deaths in T-zone       = {n_T} / {n_total}")
    print(f"deaths outside T-zone  = {n_out} / {n_total}")
    print(f"T-zone area            = {area_T:.4f}")
    print(f"outside area           = {area_out:.4f}")
    print(f"death density T-zone   = {dens_T:.4f}")
    print(f"death density outside  = {dens_out:.4f}")
    print(f"density ratio T/out    = {ratio:.4f}")


def pf_noise_diagnostic(
    deaths: np.ndarray,
    p: ModelParams,
    T_end: float,
    n_particles: int,
    area_points: np.ndarray,
    mode: str,
    sigma: float,
    repeats: int = PF_NOISE_REPEATS,
    label: str = "params",
) -> np.ndarray:
    """Repeat the same particle likelihood to estimate Monte Carlo noise."""
    lls = []
    start = time.time()
    for r in range(repeats):
        ll = particle_loglikelihood(
            death_events=deaths,
            p=p,
            T_end=T_end,
            n_particles=n_particles,
            area_points=area_points,
            seed=PF_SEED + 10000 + 1009 * r,
            mode=mode,
            sigma=sigma,
        )
        lls.append(ll)
    arr = np.asarray(lls, dtype=float)
    elapsed = time.time() - start

    print(f"\nPF noise diagnostic at {label}")
    print("--------------------------------")
    print(f"repeats = {repeats}, particles = {n_particles}, mode = {mode}, sigma = {sigma}")
    print(f"mean loglik = {np.mean(arr):.4f}")
    print(f"std  loglik = {np.std(arr, ddof=1) if repeats > 1 else 0.0:.4f}")
    print(f"min  loglik = {np.min(arr):.4f}")
    print(f"max  loglik = {np.max(arr):.4f}")
    print(f"elapsed     = {elapsed:.1f} seconds")
    return arr


def likelihood_profile_lambda_c(
    deaths: np.ndarray,
    true_params: ModelParams,
    T_end: float,
    area_points: np.ndarray,
    n_particles: int,
    mode: str,
    sigma: float,
) -> None:
    """Optional one-dimensional profile: vary lambda_a_c and keep lambda_a_T fixed."""
    grid = np.exp(np.linspace(math.log(0.005), math.log(0.5), PROFILE_GRID_SIZE))
    print("\nLikelihood profile diagnostic: lambda_a_c")
    print("-----------------------------------------")
    print("lambda_a_c, loglik")
    best_lc = None
    best_ll = -np.inf
    for lc in grid:
        p_test = replace(true_params, lambda_a_c=float(lc))
        if not valid_params(p_test):
            continue
        ll = particle_loglikelihood(
            death_events=deaths,
            p=p_test,
            T_end=T_end,
            n_particles=n_particles,
            area_points=area_points,
            seed=PF_SEED + 424242,
            mode=mode,
            sigma=sigma,
        )
        print(f"{lc:.6g}, {ll:.4f}")
        if ll > best_ll:
            best_ll = ll
            best_lc = float(lc)
    print(f"profile best lambda_a_c = {best_lc:.6g}, loglik = {best_ll:.4f}")

# ============================================================
# 8. Main demo
# ============================================================

def print_param_table(true_p: ModelParams, estimated_p: ModelParams, keys: Sequence[str]) -> None:
    print("\nParameter comparison")
    print("--------------------")
    print(f"{'parameter':<14} {'true':>12} {'estimated':>12} {'ratio est/true':>16}")
    for key in keys:
        tv = getattr(true_p, key)
        ev = getattr(estimated_p, key)
        print(f"{key:<14} {tv:12.5g} {ev:12.5g} {ev / tv:16.4g}")


def main() -> None:
    true_params = ModelParams(
        lambda_a_1=5.00,
        lambda_a_T=0.50,
        lambda_a_c=0.05,
        lambda_d=1.00,
        beta_a_R=2.50,
        beta_a_T=1.20,
        beta_d_R=2.00,
        beta_d_T=0.80,
    )

    print("Simulating synthetic death events...")
    sim = simulate_death_events(
        true_params,
        T_max=T_MAX,
        target_deaths=TARGET_DEATHS,
        seed=123,
    )
    deaths = sim["death_events"]
    final_time = float(sim["final_time"][0])

    if len(deaths) == 0:
        print("No deaths simulated. Increase T_MAX or change parameters.")
        return

    np.savetxt(
        "simulated_death_events.csv",
        deaths,
        delimiter=",",
        header="x,y,t",
        comments="",
    )

    # If we simulate a fixed physical observation window, the endpoint is T_MAX.
    # If we stop at a target number of deaths, the endpoint is the stopping time.
    if TARGET_DEATHS is None:
        T_end = T_MAX
    else:
        T_end = final_time

    print(f"  simulated deaths: {len(deaths)}")
    print(f"  raw simulator final time = {final_time:.4f}")
    print(f"  observation endpoint T_end = {T_end:.4f}")
    print(f"  crude full-area rate n/(|W|T) = {len(deaths)/(AREA_W*T_end):.5g}")
    print("  saved: simulated_death_events.csv")

    if RUN_DEATH_SPATIAL_DIAGNOSTIC:
        death_spatial_diagnostic(deaths)

    # Use a fixed set of quadrature points for diagnostics and for comparable log-likelihood calls.
    rng_area = np.random.default_rng(AREA_SEED)
    diagnostic_area_points = np.column_stack([
        rng_area.uniform(0.0, Lx, AREA_MC_POINTS),
        rng_area.uniform(0.0, Ly, AREA_MC_POINTS),
    ])

    if RUN_PF_NOISE_DIAGNOSTIC:
        pf_noise_diagnostic(
            deaths=deaths,
            p=true_params,
            T_end=T_end,
            n_particles=N_PARTICLES,
            area_points=diagnostic_area_points,
            mode=LIKELIHOOD_MODE,
            sigma=SOFT_SIGMA,
            repeats=PF_NOISE_REPEATS,
            label="true params before optimization",
        )

    if RUN_LIKELIHOOD_PROFILE:
        likelihood_profile_lambda_c(
            deaths=deaths,
            true_params=true_params,
            T_end=T_end,
            area_points=diagnostic_area_points,
            n_particles=N_PARTICLES,
            mode=LIKELIHOOD_MODE,
            sigma=SOFT_SIGMA,
        )

    # Base parameters: fixed values for non-estimated parameters.
    # In real use, replace true_params below by your chosen fixed/default values.
    base_params = true_params

    estimated_params, best_loglik = fit_parameters(
        death_events=deaths,
        base_params=base_params,
        keys=ESTIMATE_KEYS,
        T_end=T_end,
        n_particles=N_PARTICLES,
        area_mc_points=AREA_MC_POINTS,
        pf_seed=PF_SEED,
        pf_replicates=PF_REPLICATES,
        resample_method=RESAMPLE_METHOD,
        mode=LIKELIHOOD_MODE,
        sigma=SOFT_SIGMA,
        maxiter=OPT_MAXITER,
        popsize=OPT_POPSIZE,
        polish=POLISH_WITH_LBFGSB,
    )
    ll_true = particle_loglikelihood(
        death_events=deaths,
        p=true_params,
        T_end=T_end,
        n_particles=N_PARTICLES,
        area_points=diagnostic_area_points,
        seed=PF_SEED + 999,
        mode=LIKELIHOOD_MODE,
        sigma=SOFT_SIGMA,
    )

    ll_est = particle_loglikelihood(
        death_events=deaths,
        p=estimated_params,
        T_end=T_end,
        n_particles=N_PARTICLES,
        area_points=diagnostic_area_points,
        seed=PF_SEED + 999,
        mode=LIKELIHOOD_MODE,
        sigma=SOFT_SIGMA,
    )

    print("\nDiagnostic log-likelihood comparison")
    print("------------------------------------")
    print(f"loglik at true params      = {ll_true:.4f}")
    print(f"loglik at estimated params = {ll_est:.4f}")
    print(f"difference est - true      = {ll_est - ll_true:.4f}")

    if RUN_PF_NOISE_DIAGNOSTIC:
        pf_noise_diagnostic(
            deaths=deaths,
            p=estimated_params,
            T_end=T_end,
            n_particles=N_PARTICLES,
            area_points=diagnostic_area_points,
            mode=LIKELIHOOD_MODE,
            sigma=SOFT_SIGMA,
            repeats=PF_NOISE_REPEATS,
            label="estimated params after optimization",
        )

    print_param_table(true_params, estimated_params, ESTIMATE_KEYS)
    print(f"\nBest estimated particle log-likelihood: {best_loglik:.4f}")

    print("\nEstimated full parameter object:")
    print(estimated_params)

    print("\nNotes:")
    print("  1. If PF noise std is large compared with est-true loglik difference,")
    print("     increase N_PARTICLES and PF_REPLICATES before interpreting the MLE.")
    print("  2. Fixed-time simulation is recommended for cleaner point-process likelihood.")
    print("  3. Try smaller SOFT_SIGMA, then LIKELIHOOD_MODE='exact' after the soft version works.")
    print("  4. For redistribution, RESAMPLE_METHOD='residual_systematic' combines residual")
    print("     resampling with Kitagawa/systematic positions; change it for comparisons.")
    print("  5. Death-only data may not identify all caspase and ERK parameters at once;")
    print("     estimate a small subset first, then enlarge ESTIMATE_KEYS.")


if __name__ == "__main__":
    main()
