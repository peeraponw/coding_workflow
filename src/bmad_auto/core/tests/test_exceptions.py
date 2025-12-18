from bmad_auto.core import exceptions


def test_exception_hierarchy() -> None:
    assert issubclass(exceptions.ConfigurationError, exceptions.BmadAutoError)
    assert issubclass(exceptions.AgentNotFoundError, exceptions.BmadAutoError)
    assert issubclass(exceptions.AgentExecutionError, exceptions.BmadAutoError)
    assert issubclass(exceptions.AgentTimeoutError, exceptions.BmadAutoError)
    assert issubclass(exceptions.AgentOutputParseError, exceptions.BmadAutoError)
    assert issubclass(exceptions.WorkflowError, exceptions.BmadAutoError)
    assert issubclass(exceptions.EpicNotFoundError, exceptions.WorkflowError)
    assert issubclass(exceptions.StoryCreationError, exceptions.WorkflowError)
    assert issubclass(exceptions.ReviewRejectedError, exceptions.WorkflowError)
    assert issubclass(exceptions.GitOperationError, exceptions.BmadAutoError)
    assert issubclass(exceptions.StateError, exceptions.BmadAutoError)
