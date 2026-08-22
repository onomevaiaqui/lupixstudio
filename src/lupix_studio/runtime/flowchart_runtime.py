from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from lupix_studio.scene.model import SceneEntity, SceneResource


@dataclass(slots=True)
class FlowTask:
    entity_id: str
    node_id: str
    remaining: float | None = None


@dataclass(slots=True)
class EntityFlowGraph:
    entity: SceneEntity
    nodes: dict[str, dict[str, object]]
    outgoing: dict[tuple[str, str], list[str]]


class FlowchartRuntime:
    """Executa os primeiros blocos sequenciais do Flowchart."""

    def __init__(
        self,
        scene: SceneResource,
        show_message: Callable[[str, str, int], None],
        change_scene: Callable[[str, str], bool],
        play_animation: Callable[[str, str, str], bool],
    ) -> None:
        self.scene = scene
        self.show_message = show_message
        self.change_scene = change_scene
        self.play_animation = play_animation
        self.graphs: dict[str, EntityFlowGraph] = {}
        self.tasks: list[FlowTask] = []

    def start(self) -> None:
        self.tasks.clear()
        self.graphs.clear()
        for entity in self.scene.entities:
            graph = self._build_graph(entity)
            if graph is None:
                continue
            self.graphs[entity.id] = graph
            for node_id, node in graph.nodes.items():
                if str(node.get("type")) == "scene_start":
                    self._queue_outputs(entity.id, node_id, "out", self.tasks)

    def stop(self) -> None:
        self.tasks.clear()
        self.graphs.clear()

    def trigger_key(self, key_name: str) -> None:
        normalized = key_name.strip().lower()
        if not normalized:
            return
        for entity_id, graph in self.graphs.items():
            for node_id, node in graph.nodes.items():
                if (
                    str(node.get("type")) == "key_pressed"
                    and str(node.get("key", "space")).strip().lower()
                    == normalized
                ):
                    self._queue_outputs(entity_id, node_id, "out", self.tasks)

    def update(self, delta: float) -> None:
        if not self.tasks:
            return
        pending: list[FlowTask] = []
        for task in self.tasks:
            graph = self.graphs.get(task.entity_id)
            if graph is None:
                continue
            node = graph.nodes.get(task.node_id)
            if node is None:
                continue
            kind = str(node.get("type", ""))

            if kind == "wait":
                if task.remaining is None:
                    task.remaining = max(0.0, float(node.get("seconds", 1.0)))
                task.remaining -= max(0.0, delta)
                if task.remaining > 0.0:
                    pending.append(task)
                    continue
                self._queue_outputs(task.entity_id, task.node_id, "out", pending)
                continue

            if kind == "show_message":
                message = str(node.get("message_text", "Olá, mundo!")).strip()
                duration_ms = int(max(0.5, float(node.get("duration", 4.0))) * 1000)
                if message:
                    self.show_message(graph.entity.name, message, duration_ms)
                self._queue_outputs(task.entity_id, task.node_id, "out", pending)
                continue

            if kind == "play_animation":
                animation_name = str(node.get("animation_name", "")).strip()
                if animation_name:
                    self.play_animation(
                        task.entity_id,
                        graph.entity.name,
                        animation_name,
                    )
                self._queue_outputs(task.entity_id, task.node_id, "out", pending)
                continue

            if kind == "change_scene":
                target_scene = str(node.get("target_scene", "")).strip()
                if target_scene and self.change_scene(
                    graph.entity.name,
                    target_scene,
                ):
                    # A troca inicia um novo runtime e encerra este fluxo.
                    self.tasks.clear()
                    return
                self._queue_outputs(task.entity_id, task.node_id, "out", pending)
                continue

            if kind == "sequence":
                self._queue_outputs(task.entity_id, task.node_id, "then_1", pending)
                self._queue_outputs(task.entity_id, task.node_id, "then_2", pending)
                continue

            # Blocos ainda não executáveis apenas deixam o fluxo continuar.
            self._queue_outputs(task.entity_id, task.node_id, "out", pending)

        self.tasks = pending

    def _queue_outputs(
        self,
        entity_id: str,
        node_id: str,
        port: str,
        destination: list[FlowTask],
    ) -> None:
        graph = self.graphs.get(entity_id)
        if graph is None:
            return
        for target_id in graph.outgoing.get((node_id, port), []):
            destination.append(FlowTask(entity_id, target_id))

    @staticmethod
    def _build_graph(entity: SceneEntity) -> EntityFlowGraph | None:
        data = entity.blueprint
        if not isinstance(data, dict):
            return None
        raw_nodes = data.get("nodes", [])
        raw_connections = data.get("connections", [])
        if not isinstance(raw_nodes, list) or not isinstance(raw_connections, list):
            return None
        nodes = {
            str(node.get("id")): node
            for node in raw_nodes
            if isinstance(node, dict) and node.get("id")
        }
        outgoing: dict[tuple[str, str], list[str]] = {}
        for connection in raw_connections:
            if not isinstance(connection, dict):
                continue
            source_id = str(connection.get("from_node", ""))
            target_id = str(connection.get("to_node", ""))
            source_port = str(connection.get("from_port", "out"))
            if source_id not in nodes or target_id not in nodes:
                continue
            outgoing.setdefault((source_id, source_port), []).append(target_id)
        return EntityFlowGraph(entity, nodes, outgoing)
