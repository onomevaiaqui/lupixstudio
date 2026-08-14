from __future__ import annotations

from PySide6.QtCore import (
    QRect,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QApplication,
    QProxyStyle,
    QStyle,
    QStyleOption,
    QWidget,
)


class LupixCheckBoxStyle(QProxyStyle):
    """Estilo global dos checkboxes do Lupix Studio."""

    INDICATOR_SIZE = 18

    def drawPrimitive(
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget | None = None,
    ) -> None:
        if (
            element
            != QStyle.PrimitiveElement.PE_IndicatorCheckBox
        ):
            super().drawPrimitive(
                element,
                option,
                painter,
                widget,
            )

            return

        self._draw_checkbox(
            option,
            painter,
        )

    def _draw_checkbox(
        self,
        option: QStyleOption,
        painter: QPainter,
    ) -> None:
        rect = self._indicator_rect(
            option.rect
        )

        checked = bool(
            option.state
            & QStyle.StateFlag.State_On
        )

        enabled = bool(
            option.state
            & QStyle.StateFlag.State_Enabled
        )

        hovered = bool(
            option.state
            & QStyle.StateFlag.State_MouseOver
        )

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        if checked:
            background = QColor(
                "#2563eb"
            )

            border = QColor(
                "#3b82f6"
            )

        elif hovered:
            background = QColor(
                "#31353c"
            )

            border = QColor(
                "#3b82f6"
            )

        else:
            background = QColor(
                "#2a2d33"
            )

            border = QColor(
                "#5a5f68"
            )

        if not enabled:
            background.setAlpha(
                120
            )

            border.setAlpha(
                120
            )

        painter.setBrush(
            background
        )

        painter.setPen(
            QPen(
                border,
                1,
            )
        )

        painter.drawRoundedRect(
            rect,
            4,
            4,
        )

        if checked:
            self._draw_check_mark(
                painter,
                rect,
                enabled,
            )

        painter.restore()

    def _indicator_rect(
        self,
        original: QRect,
    ) -> QRect:
        size = self.INDICATOR_SIZE

        x = original.x()

        y = (
            original.y()
            + (
                original.height()
                - size
            )
            // 2
        )

        return QRect(
            x,
            y,
            size,
            size,
        )

    def _draw_check_mark(
        self,
        painter: QPainter,
        rect: QRect,
        enabled: bool,
    ) -> None:
        color = QColor(
            "#ffffff"
        )

        if not enabled:
            color.setAlpha(
                150
            )

        pen = QPen(
            color,
            2.2,
        )

        pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )

        pen.setJoinStyle(
            Qt.PenJoinStyle.RoundJoin
        )

        painter.setPen(
            pen
        )

        x = rect.left()
        y = rect.top()

        painter.drawLine(
            x + 4,
            y + 9,
            x + 8,
            y + 13,
        )

        painter.drawLine(
            x + 8,
            y + 13,
            x + 15,
            y + 5,
        )


def install_checkbox_style(
    app: QApplication,
) -> None:
    """Instala o checkbox Lupix globalmente."""

    base_style = app.style()

    style = LupixCheckBoxStyle(
        base_style
    )

    app.setStyle(
        style
    )

    app.setStyleSheet(
        app.styleSheet()
        + """
        QCheckBox {
            spacing: 7px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        """
    )