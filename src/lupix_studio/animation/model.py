from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnimationFrameRegion:
    """Região independente de um frame dentro do spritesheet."""

    x: int = 0
    y: int = 0

    width: int = 1
    height: int = 1

    offset_x: int = 0
    offset_y: int = 0

    def __post_init__(self) -> None:
        self.x = max(
            0,
            int(self.x),
        )

        self.y = max(
            0,
            int(self.y),
        )

        self.width = max(
            1,
            int(self.width),
        )

        self.height = max(
            1,
            int(self.height),
        )

        self.offset_x = int(
            self.offset_x
        )

        self.offset_y = int(
            self.offset_y
        )

    @property
    def right(self) -> int:
        return (
            self.x
            + self.width
        )

    @property
    def bottom(self) -> int:
        return (
            self.y
            + self.height
        )

    def to_dict(
        self,
    ) -> dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> AnimationFrameRegion:
        return cls(
            x=int(
                data.get(
                    "x",
                    0,
                )
            ),
            y=int(
                data.get(
                    "y",
                    0,
                )
            ),
            width=int(
                data.get(
                    "width",
                    1,
                )
            ),
            height=int(
                data.get(
                    "height",
                    1,
                )
            ),
            offset_x=int(
                data.get(
                    "offset_x",
                    0,
                )
            ),
            offset_y=int(
                data.get(
                    "offset_y",
                    0,
                )
            ),
        )


@dataclass(slots=True)
class AnimationClip:
    """Sequência de frames de uma animação."""

    name: str

    # Asset específico desta animação. Vazio = Sprite principal.
    asset_id: str = ""

    #
    # Continua sendo uma sequência de IDs inteiros.
    #
    # Isso mantém compatibilidade com:
    #
    # - Runtime atual
    # - Play Preview atual
    # - cenas antigas
    # - Animation Editor atual
    #
    frames: list[int] = field(
        default_factory=list
    )

    #
    # Cada ID pode possuir uma região independente.
    #
    # Exemplo:
    #
    # regions[0] -> primeira pose
    # regions[1] -> segunda pose
    #
    regions: dict[
        int,
        AnimationFrameRegion,
    ] = field(
        default_factory=dict
    )

    fps: float = 8.0
    loop: bool = True

    def __post_init__(self) -> None:
        self.name = (
            self.name.strip()
        )

        self.asset_id = str(self.asset_id or "").strip()

        self.frames = [
            max(
                0,
                int(frame),
            )
            for frame in self.frames
        ]

        normalized_regions: dict[
            int,
            AnimationFrameRegion,
        ] = {}

        for frame_id, region in (
            self.regions.items()
        ):
            frame_id = max(
                0,
                int(frame_id),
            )

            if isinstance(
                region,
                AnimationFrameRegion,
            ):
                normalized_regions[
                    frame_id
                ] = region

        self.regions = (
            normalized_regions
        )

        self.fps = max(
            0.01,
            float(self.fps),
        )

    @property
    def frame_duration(
        self,
    ) -> float:
        return (
            1.0
            / self.fps
        )

    def frame_at(
        self,
        elapsed: float,
    ) -> int | None:
        """
        Retorna o ID do frame atual.

        Mantemos esse comportamento para não
        quebrar o runtime existente.
        """

        if not self.frames:
            return None

        elapsed = max(
            0.0,
            elapsed,
        )

        index = int(
            elapsed
            / self.frame_duration
        )

        if self.loop:
            index %= len(
                self.frames
            )

        else:
            index = min(
                index,
                len(
                    self.frames
                ) - 1,
            )

        return self.frames[
            index
        ]

    def region(
        self,
        frame_id: int,
    ) -> AnimationFrameRegion | None:
        """Retorna a região associada ao frame."""

        return self.regions.get(
            int(frame_id)
        )

    def has_region(
        self,
        frame_id: int,
    ) -> bool:
        return (
            int(frame_id)
            in self.regions
        )

    def set_region(
        self,
        frame_id: int,
        region: AnimationFrameRegion,
    ) -> None:
        frame_id = max(
            0,
            int(frame_id),
        )

        self.regions[
            frame_id
        ] = region

    def remove_region(
        self,
        frame_id: int,
    ) -> bool:
        frame_id = int(
            frame_id
        )

        if frame_id not in self.regions:
            return False

        del self.regions[
            frame_id
        ]

        return True

    def clear_regions(
        self,
    ) -> None:
        self.regions.clear()

    def next_region_id(
        self,
    ) -> int:
        """
        Retorna um ID livre para uma nova pose.
        """

        used_ids = set(
            self.regions
        )

        used_ids.update(
            self.frames
        )

        frame_id = 0

        while frame_id in used_ids:
            frame_id += 1

        return frame_id

    def add_region_frame(
        self,
        region: AnimationFrameRegion,
    ) -> int:
        """
        Cria uma região e adiciona seu ID ao
        final da sequência da animação.
        """

        frame_id = (
            self.next_region_id()
        )

        self.set_region(
            frame_id,
            region,
        )

        self.frames.append(
            frame_id
        )

        return frame_id

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "name": self.name,
            "asset_id": self.asset_id,
            "frames": list(
                self.frames
            ),
            "regions": {
                str(frame_id): (
                    region.to_dict()
                )
                for frame_id, region
                in self.regions.items()
            },
            "fps": self.fps,
            "loop": self.loop,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> AnimationClip:
        raw_frames = data.get(
            "frames",
            [],
        )

        frames: list[int] = []

        if isinstance(
            raw_frames,
            list,
        ):
            frames = [
                max(
                    0,
                    int(frame),
                )
                for frame in raw_frames
            ]

        regions: dict[
            int,
            AnimationFrameRegion,
        ] = {}

        raw_regions = data.get(
            "regions",
            {},
        )

        if isinstance(
            raw_regions,
            dict,
        ):
            for (
                raw_frame_id,
                raw_region,
            ) in raw_regions.items():
                if not isinstance(
                    raw_region,
                    dict,
                ):
                    continue

                try:
                    frame_id = max(
                        0,
                        int(
                            raw_frame_id
                        ),
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                regions[
                    frame_id
                ] = (
                    AnimationFrameRegion.from_dict(
                        dict(
                            raw_region
                        )
                    )
                )

        return cls(
            name=str(
                data.get(
                    "name",
                    "animation",
                )
            ),
            asset_id=str(
                data.get(
                    "asset_id",
                    "",
                )
                or ""
            ),
            frames=frames,
            regions=regions,
            fps=float(
                data.get(
                    "fps",
                    8.0,
                )
            ),
            loop=bool(
                data.get(
                    "loop",
                    True,
                )
            ),
        )


@dataclass(slots=True)
class AnimationComponent:
    """Configuração de animações de uma entidade."""

    enabled: bool = True

    #
    # Modo de definição dos frames:
    #
    # regions
    #     seleção livre de poses completas
    #
    # grid
    #     grade tradicional
    #
    frame_mode: str = "regions"

    #
    # Mantidos para o modo Grid e para
    # compatibilidade com projetos antigos.
    #
    frame_width: int = 16
    frame_height: int = 16

    default_animation: str = "idle"

    clips: dict[
        str,
        AnimationClip,
    ] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.frame_width = max(
            1,
            int(
                self.frame_width
            ),
        )

        self.frame_height = max(
            1,
            int(
                self.frame_height
            ),
        )

        frame_mode = (
            str(
                self.frame_mode
            )
            .strip()
            .lower()
        )

        if frame_mode not in {
            "regions",
            "grid",
        }:
            frame_mode = "regions"

        self.frame_mode = frame_mode

        self.default_animation = (
            self.default_animation.strip()
            or "idle"
        )

    def add_clip(
        self,
        clip: AnimationClip,
    ) -> None:
        if not clip.name:
            return

        self.clips[
            clip.name
        ] = clip

    def remove_clip(
        self,
        name: str,
    ) -> bool:
        if name not in self.clips:
            return False

        del self.clips[
            name
        ]

        return True

    def clip(
        self,
        name: str,
    ) -> AnimationClip | None:
        return self.clips.get(
            name
        )

    def default_clip(
        self,
    ) -> AnimationClip | None:
        clip = self.clip(
            self.default_animation
        )

        if clip is not None:
            return clip

        if not self.clips:
            return None

        return next(
            iter(
                self.clips.values()
            )
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "frame_mode": self.frame_mode,
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
            "default_animation": (
                self.default_animation
            ),
            "clips": {
                name: clip.to_dict()
                for name, clip
                in self.clips.items()
            },
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, object],
    ) -> AnimationComponent:
        #
        # Projetos antigos não possuem frame_mode.
        #
        # Neles usamos grid para preservar exatamente
        # o comportamento anterior.
        #
        frame_mode = data.get(
            "frame_mode"
        )

        if frame_mode is None:
            frame_mode = "grid"

        component = cls(
            enabled=bool(
                data.get(
                    "enabled",
                    True,
                )
            ),
            frame_mode=str(
                frame_mode
            ),
            frame_width=int(
                data.get(
                    "frame_width",
                    16,
                )
            ),
            frame_height=int(
                data.get(
                    "frame_height",
                    16,
                )
            ),
            default_animation=str(
                data.get(
                    "default_animation",
                    "idle",
                )
            ),
        )

        raw_clips = data.get(
            "clips",
            {},
        )

        if not isinstance(
            raw_clips,
            dict,
        ):
            return component

        for (
            name,
            raw_clip,
        ) in raw_clips.items():
            if not isinstance(
                raw_clip,
                dict,
            ):
                continue

            clip_data = dict(
                raw_clip
            )

            clip_data[
                "name"
            ] = str(
                name
            )

            clip = (
                AnimationClip.from_dict(
                    clip_data
                )
            )

            component.add_clip(
                clip
            )

        return component