from typing import Iterable, Optional

import numpy as np

import bmi.samplers.api as samplers
from bmi.benchmark.core import Task, generate_task


def task_student_uniform(
    dim_x: int,
    dim_y: int,
    df: int,
    n_samples: int,
    n_seeds: int,
) -> Task:
    sampler = samplers.SplitStudentT(
        dim_x=dim_x,
        dim_y=dim_y,
        dispersion=np.eye(dim_x + dim_y) * 0.5 + 0.5,
        df=df,
    )

    task = generate_task(
        sampler=sampler,
        n_samples=n_samples,
        seeds=range(n_seeds),
        task_id=f"student-uniform-{dim_x}-{dim_y}-{df}-{n_samples}",
        task_params=dict(
            degrees_of_freedom=df,
        ),
    )

    return task


def task_student_sparse(
    dim_x: int,
    dim_y: int,
    df: int,
    n_seeds: int,
    n_samples: int,
    dispersion_signal: float = 0.8,
    dispersion_noise: float = 0.1,
    task_id: Optional[str] = None,
) -> Task:
    dispersion = samplers.parametrised_correlation_matrix(
        dim_x=dim_x,
        dim_y=dim_y,
        k=2,
        correlation=dispersion_signal,
        correlation_x=dispersion_noise,
        correlation_y=dispersion_noise,
    )

    sampler = samplers.SplitStudentT(
        dim_x=dim_x,
        dim_y=dim_y,
        dispersion=dispersion,
        df=df,
    )

    default_task_id = f"student-sparse-{dim_x}-{dim_y}-{df}-{n_samples}"
    task_id = task_id if task_id is not None else default_task_id
    task = generate_task(
        sampler=sampler,
        n_samples=n_samples,
        seeds=range(n_seeds),
        task_id=task_id,
        task_params=dict(
            dispersion_signal=dispersion_signal,
            dispersion_noise=dispersion_noise,
            degrees_of_freedom=df,
        ),
    )

    return task


def _generate_uniform(n_seeds: int, n_samples: int = 5000) -> Iterable[Task]:
    """Uniform dispersion matrix."""

    # Covariance for df=2 doesn't exist! Let's see how this goes...
    yield task_student_uniform(dim_x=5, dim_y=5, df=2, n_samples=n_samples, n_seeds=n_seeds)

    # Larger df have covariance
    yield task_student_uniform(dim_x=5, dim_y=5, df=3, n_samples=n_samples, n_seeds=n_seeds)
    yield task_student_uniform(dim_x=5, dim_y=5, df=5, n_samples=n_samples, n_seeds=n_seeds)
    yield task_student_uniform(dim_x=5, dim_y=5, df=10, n_samples=n_samples, n_seeds=n_seeds)
    yield task_student_uniform(dim_x=5, dim_y=5, df=30, n_samples=n_samples, n_seeds=n_seeds)

    # Different dimensions with df = 5
    yield task_student_uniform(dim_x=2, dim_y=2, df=5, n_samples=n_samples, n_seeds=n_seeds)
    yield task_student_uniform(dim_x=25, dim_y=25, df=5, n_samples=n_samples, n_seeds=n_seeds)


def _generate_sparse(n_seeds: int, n_samples: int = 5000) -> Iterable[Task]:
    """Sparse dispersion matrix."""
    yield task_student_sparse(dim_x=3, dim_y=3, df=5, n_samples=n_samples, n_seeds=n_seeds)
    yield task_student_sparse(dim_x=2, dim_y=5, df=5, n_samples=n_samples, n_seeds=n_seeds)
    yield task_student_sparse(dim_x=5, dim_y=5, df=5, n_samples=n_samples, n_seeds=n_seeds)


def generate_tasks(n_seeds: int) -> Iterable[Task]:
    yield from _generate_uniform(n_seeds)
    yield from _generate_sparse(n_seeds)
