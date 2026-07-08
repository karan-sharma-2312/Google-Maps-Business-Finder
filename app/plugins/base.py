"""Plugin system interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod


class PluginContext(dict):
    """Shared plugin context object."""


class Plugin(ABC):
    """Base contract for custom plugins."""

    name: str = "base-plugin"

    @abstractmethod
    async def run(self, context: PluginContext) -> dict:
        """Execute plugin and return result payload."""


class PluginManager:
    """Registry and execution manager for plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.name] = plugin

    async def execute(self, name: str, context: PluginContext) -> dict:
        plugin = self._plugins[name]
        return await plugin.run(context)
