from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field, Factory
from griptape.artifacts import BaseArtifact
from griptape.core import ActivityMixin


@define
class BaseToolMemory(ActivityMixin, ABC):
    id: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    def process_input(self, tool_activity: callable, value: Optional[dict]) -> Optional[dict]:
        return self.load_artifacts(value)

    def process_output(self, tool_activity: callable, artifact: BaseArtifact) -> BaseArtifact:
        return artifact

    def load_artifacts(self, value: Optional[dict]) -> Optional[dict]:
        namespaces = []

        if value:
            sources = value.get("artifacts", {}).get("sources", [])

            for source in sources:
                if source["memory_id"] == self.id:
                    namespaces.extend(source["artifact_namespaces"])

        if len(namespaces) > 0:
            new_value = value.copy()

            if not new_value.get("artifacts", {}).get("values"):
                new_value.update({"artifacts": {"values": []}})

            for namespace in namespaces:
                [
                    new_value["artifacts"]["values"].append(a.to_dict())
                    for a in self.load_namespace_artifacts(namespace)
                ]

            return new_value
        else:
            return value

    @abstractmethod
    def load_namespace_artifacts(self, namespace: str) -> list[BaseArtifact]:
        ...
    