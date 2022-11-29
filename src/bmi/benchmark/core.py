from typing import Generator, Iterable, Optional, Tuple, Union

import pandas as pd
import pydantic

import bmi.benchmark._serialize as se
from bmi.interface import ISampler


class TaskMetadata(pydantic.BaseModel):
    task_id: str
    dim_x: int
    dim_y: int
    n_samples: int
    mi_true: pydantic.NonNegativeFloat


class Task:
    def __init__(
        self, metadata: TaskMetadata, samples: Union[se.SamplesDict, pd.DataFrame]
    ) -> None:
        self.metadata = metadata
        # TODO(Pawel): Add dimension validation if dictionary is passed, rather than a data frame
        self._samples: se.SamplesDict = (
            se.dataframe_to_dict(samples, dim_x=metadata.dim_x, dim_y=metadata.dim_y)
            if isinstance(samples, pd.DataFrame)
            else samples
        )

    def __getitem__(self, item: se.Seed) -> se.SamplesXY:
        return self._samples[item]

    def __iter__(self) -> Generator[Tuple[se.Seed, se.SamplesXY], None, None]:
        for seed, vals in self._samples.items():
            yield seed, vals

    @property
    def task_id(self) -> str:
        return self.metadata.task_id

    @property
    def dim_x(self) -> int:
        return self.metadata.dim_x

    @property
    def dim_y(self) -> int:
        return self.metadata.dim_y

    @property
    def mi_true(self) -> float:
        return self.metadata.mi_true

    @property
    def n_samples(self) -> int:
        return self.metadata.n_samples

    def save(self, path: se.Pathlike, exist_ok: bool = False) -> None:
        task_directory = se.TaskDirectory(path)
        # TODO(Pawel): Should we use the default values
        #  for prefix names or leave this configurable?
        df = se.dict_to_dataframe(self._samples)
        task_directory.save(metadata=self.metadata, samples=df, exist_ok=exist_ok)

    @classmethod
    def load(cls, path: se.Pathlike) -> "Task":
        task_directory = se.TaskDirectory(path)

        metadata = TaskMetadata(**task_directory.load_metadata())
        samples_df: pd.DataFrame = task_directory.load_samples()

        return cls(
            metadata=metadata,
            samples=samples_df,
        )


def generate_task(sampler: ISampler, n_samples: int, seeds: Iterable[int], task_id: str) -> Task:
    metadata = TaskMetadata(
        task_id=task_id,
        dim_x=sampler.dim_x,
        dim_y=sampler.dim_y,
        n_samples=n_samples,
        mi_true=sampler.mutual_information(),
    )

    samples = {seed: sampler.sample(n_points=n_samples, rng=seed) for seed in seeds}

    return Task(
        metadata=metadata,
        samples=samples,
    )


class RunResult(pydantic.BaseModel):
    """Class keeping the output of a single estimator run."""

    task_id: str
    seed: se.Seed
    estimator_id: str
    mi_estimate: float
    time_in_seconds: Optional[float] = None
    estimator_params: Optional[dict] = None
