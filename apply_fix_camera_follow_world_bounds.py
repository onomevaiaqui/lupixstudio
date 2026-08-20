import re
import shutil
from pathlib import Path

PATH = Path(r".\src\lupix_studio\ui\play_preview.py")

if not PATH.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {PATH}")

backup = PATH.with_suffix(PATH.suffix + ".bak_camera_follow_world_bounds")
if not backup.exists():
    shutil.copy2(PATH, backup)

text = PATH.read_text(encoding="utf-8")

old_scene_rect = """        self.graphics_scene.setSceneRect(
            QRectF(
                0,
                0,
                scene.width,
                scene.height,
            )
        )
"""

new_scene_rect = """        world_left = self.runtime.world_left
        world_top = self.runtime.world_top
        world_right = self.runtime.world_right
        world_bottom = self.runtime.world_bottom

        world_width = max(
            1.0,
            world_right - world_left,
        )
        world_height = max(
            1.0,
            world_bottom - world_top,
        )

        self.graphics_scene.setSceneRect(
            QRectF(
                world_left,
                world_top,
                world_width,
                world_height,
            )
        )
"""

if old_scene_rect in text:
    text = text.replace(old_scene_rect, new_scene_rect, 1)

old_background = """        background = QGraphicsRectItem(
            0,
            0,
            scene.width,
            scene.height,
        )
"""

new_background = """        background = QGraphicsRectItem(
            world_left,
            world_top,
            world_width,
            world_height,
        )
"""

if old_background in text:
    text = text.replace(old_background, new_background, 1)

fit_scene_pattern = re.compile(
    r"    def fit_scene\(self\) -> None:\n"
    r".*?"
    r"(?=\n    def fit_camera\(self\) -> None:)",
    re.DOTALL,
)
fit_scene_match = fit_scene_pattern.search(text)
if fit_scene_match is None:
    raise RuntimeError("Não foi possível localizar fit_scene().")

fit_scene_new = """    def fit_scene(self) -> None:
        if self.runtime is None:
            return

        self.follow_active_camera = False

        world_left = self.runtime.world_left
        world_top = self.runtime.world_top
        world_right = self.runtime.world_right
        world_bottom = self.runtime.world_bottom

        self.fitInView(
            QRectF(
                world_left,
                world_top,
                max(1.0, world_right - world_left),
                max(1.0, world_bottom - world_top),
            ),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
"""

text = text[:fit_scene_match.start()] + fit_scene_new + text[fit_scene_match.end():]

fit_camera_pattern = re.compile(
    r"    def fit_camera\(self\) -> None:\n"
    r".*?"
    r"(?=\n    def use_active_camera\(self\) -> None:)",
    re.DOTALL,
)
fit_camera_match = fit_camera_pattern.search(text)
if fit_camera_match is None:
    raise RuntimeError("Não foi possível localizar fit_camera().")

fit_camera_new = """    def fit_camera(self) -> None:
        if self.runtime is None:
            return

        scene = self.runtime.scene
        camera_entity = scene.active_camera()

        if camera_entity is None or camera_entity.camera is None:
            self.fit_scene()
            return

        camera = camera_entity.camera
        zoom = max(0.01, float(camera.zoom))
        visible_width = max(1.0, float(camera.width) / zoom)
        visible_height = max(1.0, float(camera.height) / zoom)

        player = self.runtime.player
        if player is not None:
            target_x = player.transform.x
            target_y = player.transform.y
        else:
            target_x = camera_entity.transform.x
            target_y = camera_entity.transform.y

        world_left = self.runtime.world_left
        world_top = self.runtime.world_top
        world_right = self.runtime.world_right
        world_bottom = self.runtime.world_bottom

        world_width = max(1.0, world_right - world_left)
        world_height = max(1.0, world_bottom - world_top)

        if visible_width < world_width:
            half_width = visible_width / 2.0
            center_x = max(
                world_left + half_width,
                min(world_right - half_width, target_x),
            )
        else:
            center_x = (world_left + world_right) / 2.0
            visible_width = world_width

        if visible_height < world_height:
            half_height = visible_height / 2.0
            center_y = max(
                world_top + half_height,
                min(world_bottom - half_height, target_y),
            )
        else:
            center_y = (world_top + world_bottom) / 2.0
            visible_height = world_height

        camera_rect = QRectF(
            center_x - visible_width / 2.0,
            center_y - visible_height / 2.0,
            visible_width,
            visible_height,
        )

        self.fitInView(
            camera_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.centerOn(center_x, center_y)
"""

text = text[:fit_camera_match.start()] + fit_camera_new + text[fit_camera_match.end():]
PATH.write_text(text, encoding="utf-8")

print("Correção de câmera aplicada.")
print("- câmera ativa segue automaticamente o Player")
print("- respeita width/height/zoom")
print("- usa os limites reais do mundo")
print("- para corretamente nas bordas da fase")
print("- o Player continua andando até o final do mapa")
print(f"Backup: {backup}")
