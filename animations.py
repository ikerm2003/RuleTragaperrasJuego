"""
Enhanced Animation System for Casino Game
Provides card flip, chip movement, and other advanced animations
"""

from typing import Callable, Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSequentialAnimationGroup,
    Qt,
)
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QLabel, QWidget


class AnimationManager:
    """Manages enhanced animations"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.active_animations = []

    def is_enabled(self) -> bool:
        """Check if animations are enabled"""
        return self.config.get("interface", "card_animation_enabled", True)

    def get_duration_multiplier(self) -> float:
        """Get animation speed multiplier"""
        return self.config.get_animation_speed()

    def create_card_flip_animation(
        self,
        label: QLabel,
        from_pixmap: QPixmap,
        to_pixmap: QPixmap,
        duration: int = 300,
        on_complete: Optional[Callable] = None,
    ) -> QSequentialAnimationGroup:
        """
        Create a card flip animation

        Args:
            label: QLabel to animate
            from_pixmap: Initial pixmap (back of card)
            to_pixmap: Final pixmap (front of card)
            duration: Animation duration in ms
            on_complete: Callback when animation completes
        """
        duration = int(duration * self.get_duration_multiplier())

        group = QSequentialAnimationGroup()

        # First half: shrink horizontally to simulate first half of flip
        shrink = QPropertyAnimation(label, b"geometry")
        shrink.setDuration(duration // 2)
        shrink.setEasingCurve(QEasingCurve.Type.InOutQuad)

        original_rect = label.geometry()
        mid_rect = QRect(
            original_rect.x() + original_rect.width() // 4,
            original_rect.y(),
            original_rect.width() // 2,
            original_rect.height(),
        )

        shrink.setStartValue(original_rect)
        shrink.setEndValue(mid_rect)

        # Change pixmap at midpoint
        def change_pixmap():
            label.setPixmap(
                to_pixmap.scaled(
                    label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        shrink.finished.connect(change_pixmap)
        group.addAnimation(shrink)

        # Second half: expand back to full size
        expand = QPropertyAnimation(label, b"geometry")
        expand.setDuration(duration // 2)
        expand.setEasingCurve(QEasingCurve.Type.InOutQuad)
        expand.setStartValue(mid_rect)
        expand.setEndValue(original_rect)
        group.addAnimation(expand)

        if on_complete:
            group.finished.connect(on_complete)

        return group

    def create_chip_movement_animation(
        self,
        widget: QWidget,
        from_pos: QPoint,
        to_pos: QPoint,
        duration: int = 500,
        on_complete: Optional[Callable] = None,
    ) -> QPropertyAnimation:
        """
        Create chip movement animation

        Args:
            widget: Widget to animate
            from_pos: Starting position
            to_pos: Ending position
            duration: Animation duration in ms
            on_complete: Callback when animation completes
        """
        duration = int(duration * self.get_duration_multiplier())

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(from_pos)
        anim.setEndValue(to_pos)

        if on_complete:
            anim.finished.connect(on_complete)

        return anim

    def create_fade_in_animation(
        self,
        widget: QWidget,
        duration: int = 300,
        on_complete: Optional[Callable] = None,
    ) -> QPropertyAnimation:
        """
        Create fade in animation

        Args:
            widget: Widget to fade in
            duration: Animation duration in ms
            on_complete: Callback when animation completes
        """
        duration = int(duration * self.get_duration_multiplier())

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if on_complete:
            anim.finished.connect(on_complete)

        return anim

    def create_fade_out_animation(
        self,
        widget: QWidget,
        duration: int = 300,
        on_complete: Optional[Callable] = None,
    ) -> QPropertyAnimation:
        """
        Create fade out animation

        Args:
            widget: Widget to fade out
            duration: Animation duration in ms
            on_complete: Callback when animation completes
        """
        duration = int(duration * self.get_duration_multiplier())

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if on_complete:
            anim.finished.connect(on_complete)

        return anim

    def create_bounce_animation(
        self, widget: QWidget, amount: int = 10, duration: int = 200
    ) -> QSequentialAnimationGroup:
        """
        Create bounce animation

        Args:
            widget: Widget to bounce
            amount: Bounce distance in pixels
            duration: Total animation duration in ms
        """
        duration = int(duration * self.get_duration_multiplier())

        group = QSequentialAnimationGroup()
        original_pos = widget.pos()

        # Bounce up
        up = QPropertyAnimation(widget, b"pos")
        up.setDuration(duration // 2)
        up.setEasingCurve(QEasingCurve.Type.OutCubic)
        up.setStartValue(original_pos)
        up.setEndValue(QPoint(original_pos.x(), original_pos.y() - amount))
        group.addAnimation(up)

        # Bounce down
        down = QPropertyAnimation(widget, b"pos")
        down.setDuration(duration // 2)
        down.setEasingCurve(QEasingCurve.Type.InCubic)
        down.setStartValue(QPoint(original_pos.x(), original_pos.y() - amount))
        down.setEndValue(original_pos)
        group.addAnimation(down)

        return group

    def create_scale_pulse_animation(
        self, widget: QWidget, scale_factor: float = 1.1, duration: int = 300
    ) -> QSequentialAnimationGroup:
        """
        Create scale pulse animation (grow and shrink)

        Args:
            widget: Widget to animate
            scale_factor: How much to scale (1.1 = 110%)
            duration: Total animation duration in ms
        """
        duration = int(duration * self.get_duration_multiplier())

        group = QSequentialAnimationGroup()
        original_rect = widget.geometry()

        # Calculate scaled size
        center_x = original_rect.x() + original_rect.width() // 2
        center_y = original_rect.y() + original_rect.height() // 2

        scaled_width = int(original_rect.width() * scale_factor)
        scaled_height = int(original_rect.height() * scale_factor)

        scaled_rect = QRect(
            center_x - scaled_width // 2,
            center_y - scaled_height // 2,
            scaled_width,
            scaled_height,
        )

        # Scale up
        scale_up = QPropertyAnimation(widget, b"geometry")
        scale_up.setDuration(duration // 2)
        scale_up.setEasingCurve(QEasingCurve.Type.OutCubic)
        scale_up.setStartValue(original_rect)
        scale_up.setEndValue(scaled_rect)
        group.addAnimation(scale_up)

        # Scale down
        scale_down = QPropertyAnimation(widget, b"geometry")
        scale_down.setDuration(duration // 2)
        scale_down.setEasingCurve(QEasingCurve.Type.InCubic)
        scale_down.setStartValue(scaled_rect)
        scale_down.setEndValue(original_rect)
        group.addAnimation(scale_down)

        return group

    def create_slide_in_animation(
        self, widget: QWidget, direction: str = "left", duration: int = 400
    ) -> QPropertyAnimation:
        """
        Create slide in animation

        Args:
            widget: Widget to slide in
            direction: Direction to slide from ("left", "right", "top", "bottom")
            duration: Animation duration in ms
        """
        duration = int(duration * self.get_duration_multiplier())

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        final_pos = widget.pos()
        widget_parent = widget.parent()

        if direction == "left":
            start_pos = QPoint(-widget.width(), final_pos.y())
        elif direction == "right":
            parent_width = (
                widget_parent.width() if isinstance(widget_parent, QWidget) else 800
            )
            start_pos = QPoint(parent_width, final_pos.y())
        elif direction == "top":
            start_pos = QPoint(final_pos.x(), -widget.height())
        else:  # bottom
            parent_height = (
                widget_parent.height() if isinstance(widget_parent, QWidget) else 600
            )
            start_pos = QPoint(final_pos.x(), parent_height)

        anim.setStartValue(start_pos)
        anim.setEndValue(final_pos)

        return anim

    def create_victory_animation(
        self, widget: QWidget, duration: int = 1000
    ) -> QParallelAnimationGroup:
        """
        Create victory celebration animation (scale + fade effects)

        Args:
            widget: Widget to animate
            duration: Total animation duration in ms
        """
        duration = int(duration * self.get_duration_multiplier())

        group = QParallelAnimationGroup()

        # Pulsing scale animation
        scale_anim = self.create_scale_pulse_animation(widget, 1.2, duration)
        group.addAnimation(scale_anim)

        return group

    def stop_all_animations(self):
        """Stop all active animations"""
        for anim in self.active_animations:
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        self.active_animations.clear()


# Global animation manager instance
_animation_manager: Optional[AnimationManager] = None


def get_animation_manager(config_manager=None):
    """Get the global animation manager instance"""
    global _animation_manager
    if _animation_manager is None and config_manager is not None:
        _animation_manager = AnimationManager(config_manager)
    return _animation_manager
