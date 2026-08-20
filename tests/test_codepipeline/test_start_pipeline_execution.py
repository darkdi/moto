from uuid import UUID

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws
from moto.codepipeline.models import CodePipeline, codepipeline_backends
from moto.core import DEFAULT_ACCOUNT_ID

REGION = "us-east-1"
PIPELINE_NAME = "test-pipeline"


def _seed_pipeline() -> CodePipeline:
    backend = codepipeline_backends[DEFAULT_ACCOUNT_ID][REGION]
    pipeline = CodePipeline(
        DEFAULT_ACCOUNT_ID,
        REGION,
        {"name": PIPELINE_NAME, "stages": []},
    )
    backend.pipelines[PIPELINE_NAME] = pipeline
    return pipeline


@mock_aws
def test_start_pipeline_execution() -> None:
    pipeline = _seed_pipeline()
    client = boto3.client("codepipeline", region_name=REGION)

    first = client.start_pipeline_execution(name=PIPELINE_NAME)["pipelineExecutionId"]
    second = client.start_pipeline_execution(name=PIPELINE_NAME)["pipelineExecutionId"]

    assert str(UUID(first)) == first
    assert str(UUID(second)) == second
    assert first != second
    assert pipeline.execution_ids == [first, second]


@mock_aws
def test_start_pipeline_execution_unknown_pipeline() -> None:
    client = boto3.client("codepipeline", region_name=REGION)

    with pytest.raises(ClientError) as exc:
        client.start_pipeline_execution(name="missing-pipeline")

    assert exc.value.response["Error"]["Code"] == "PipelineNotFoundException"
