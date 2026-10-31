"""Reference solutions. Every task has TWO independent methods that must agree.

Solution A is analytic (SymPy or a closed form). Solution B is numerical (SciPy/NumPy/mpmath).
A task is only valid when both give the same number. This catches wrong reference answers,
which is the most expensive kind of mistake in a benchmark.
"""
import math
from dataclasses import dataclass
from typing import Callable

import mpmath
import numpy as np
import sympy as sp
from scipy import integrate, special


@dataclass(frozen=True)
class Reference:
    solution_a: Callable[[], float]
    solution_b: Callable[[], float]
    cross_check_rel_tol: float = 1e-6


# ---------- physics ----------

def p001_a():
    v0, angle, g = 30.0, math.radians(40.0), 9.81
    t = sp.symbols("t", positive=True)
    flight_time = sp.solve(sp.Eq(v0 * sp.sin(angle) * t - g * t**2 / 2, 0), t)[0]
    return float(v0 * math.cos(angle) * flight_time)


def p001_b():
    v0, angle, g = 30.0, math.radians(40.0), 9.81

    def motion(_, state):
        return [state[2], state[3], 0.0, -g]

    def hit_ground(_, state):
        return state[1]

    hit_ground.terminal = True
    hit_ground.direction = -1
    result = integrate.solve_ivp(
        motion, (0, 20), [0, 0, v0 * math.cos(angle), v0 * math.sin(angle)],
        events=hit_ground, rtol=1e-11, atol=1e-12,
    )
    return float(result.y_events[0][0][0])


def p002_a():
    length, theta0, g = 1.0, math.radians(60.0), 9.81
    return float(4 * math.sqrt(length / g) * special.ellipk(math.sin(theta0 / 2) ** 2))


def p002_b():
    length, theta0, g = 1.0, math.radians(60.0), 9.81

    def pendulum(_, state):
        return [state[1], -(g / length) * math.sin(state[0])]

    def crosses_zero(_, state):
        return state[0]

    crosses_zero.terminal = True
    crosses_zero.direction = -1
    result = integrate.solve_ivp(
        pendulum, (0, 10), [theta0, 0.0], events=crosses_zero, rtol=1e-12, atol=1e-13
    )
    return float(4 * result.t_events[0][0])


def p003_a():
    t = sp.symbols("t", positive=True)
    t_env, t0, k, target = 20, 90, sp.Rational(5, 100), 40
    solution = sp.solve(sp.Eq(t_env + (t0 - t_env) * sp.exp(-k * t), target), t)[0]
    return float(solution)


def p003_b():
    def cooling(_, temp):
        return [-0.05 * (temp[0] - 20.0)]

    def reaches_target(_, temp):
        return temp[0] - 40.0

    reaches_target.terminal = True
    reaches_target.direction = -1
    result = integrate.solve_ivp(
        cooling, (0, 200), [90.0], events=reaches_target, rtol=1e-12, atol=1e-12
    )
    return float(result.t_events[0][0])


def p004_a():
    x = sp.symbols("x")
    density = 2 * sp.sin(2 * sp.pi * x) ** 2
    return float(sp.integrate(density, (x, 0, sp.Rational(1, 3))))


def p004_b():
    value, _ = integrate.quad(lambda x: 2 * math.sin(2 * math.pi * x) ** 2, 0, 1 / 3)
    return float(value)


def p005_a():
    ve, m0, mdot, burn, g = 2500.0, 1000.0, 10.0, 60.0, 9.81
    return ve * math.log(m0 / (m0 - mdot * burn)) - g * burn


def p005_b():
    ve, m0, mdot, burn, g = 2500.0, 1000.0, 10.0, 60.0, 9.81

    def acceleration(t, _):
        return [ve * mdot / (m0 - mdot * t) - g]

    result = integrate.solve_ivp(acceleration, (0, burn), [0.0], rtol=1e-12, atol=1e-12)
    return float(result.y[0][-1])


def p006_a():
    electron_rest_energy_mev = 0.51099895
    gamma = 1 / math.sqrt(1 - 0.8**2)
    return float((gamma - 1) * electron_rest_energy_mev)


def p006_b():
    electron_rest_energy_mev = 0.51099895
    # Work-energy: kinetic energy = integral of v dp, with p = gamma*m*v, in units where c = 1.
    value, _ = integrate.quad(lambda b: b * (1 - b**2) ** -1.5, 0, 0.8)
    return float(value * electron_rest_energy_mev)


# ---------- mathematics ----------

def m001_a():
    x = sp.symbols("x")
    return float(sp.integrate(x * sp.sin(x), (x, 0, sp.pi)))


def m001_b():
    value, _ = integrate.quad(lambda x: x * math.sin(x), 0, math.pi)
    return float(value)


def m002_a():
    n = sp.symbols("n", integer=True, positive=True)
    return float(sp.summation(1 / n**2, (n, 1, sp.oo)))


def m002_b():
    count = 10**6
    terms = 1.0 / np.arange(1, count + 1, dtype=np.float64) ** 2
    # Euler-Maclaurin estimate of the tail beyond `count`
    tail = 1 / count - 1 / (2 * count**2) + 1 / (6 * count**3)
    return float(np.sum(terms[::-1]) + tail)


def m003_a():
    matrix = sp.Matrix([[4, 1], [2, 3]])
    return float(max(matrix.eigenvals()))


def m003_b():
    eigenvalues = np.linalg.eigvals(np.array([[4.0, 1.0], [2.0, 3.0]]))
    return float(np.max(eigenvalues.real))


def m004_a():
    x = sp.symbols("x")
    roots = sp.solve(x**3 - 6 * x**2 + 11 * x - 6, x)
    return float(sum(r**2 for r in roots))


def m004_b():
    roots = np.roots([1, -6, 11, -6])
    return float(np.sum(roots.real**2))


def m005_a():
    from_start, one_head = sp.symbols("from_start one_head")
    solution = sp.solve(
        [
            sp.Eq(from_start, 1 + sp.Rational(1, 2) * one_head + sp.Rational(1, 2) * from_start),
            sp.Eq(one_head, 1 + sp.Rational(1, 2) * from_start),
        ],
        [from_start, one_head],
    )
    return float(solution[from_start])


def m005_b():
    transient = np.array([[0.5, 0.5], [0.5, 0.0]])  # states: no head yet, one head
    fundamental = np.linalg.inv(np.eye(2) - transient)
    return float(fundamental[0].sum())


def m006_a():
    x = sp.symbols("x")
    return float(sp.limit((sp.sin(x) - x) / x**3, x, 0))


def m006_b():
    mpmath.mp.dps = 50
    x = mpmath.mpf("1e-5")
    return float((mpmath.sin(x) - x) / x**3)


REGISTRY = {
    "P-001": Reference(p001_a, p001_b),
    "P-002": Reference(p002_a, p002_b),
    "P-003": Reference(p003_a, p003_b),
    "P-004": Reference(p004_a, p004_b),
    "P-005": Reference(p005_a, p005_b),
    "P-006": Reference(p006_a, p006_b),
    "M-001": Reference(m001_a, m001_b),
    "M-002": Reference(m002_a, m002_b, cross_check_rel_tol=1e-9),
    "M-003": Reference(m003_a, m003_b),
    "M-004": Reference(m004_a, m004_b),
    "M-005": Reference(m005_a, m005_b),
    "M-006": Reference(m006_a, m006_b, cross_check_rel_tol=1e-8),
}
