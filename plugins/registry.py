"""Sistema central de auto-discovery e carregamento de plugins.

Cada plugin vive em plugins/<categoria>/<nome>/ e expõe um plugin.yaml com:
  name: identificador usado em ENABLED_*_PLUGINS
  entry_point: "modulo.pontilhado:NomeDaClasse"
  category: sources | ai | notifications | reports | exports

O Core e os Agents nunca importam um plugin concreto por nome de módulo fixo —
tudo passa por load_plugin()/load_enabled(), o que permite habilitar/desabilitar
qualquer plugin apenas mudando ENABLED_*_PLUGINS no .env, sem tocar em código (OCP).
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog
import yaml

from opportunity_squad.core.exceptions import PluginLoadError, PluginNotFoundError

logger = structlog.get_logger("plugins.registry")

PLUGINS_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PluginManifest:
    name: str
    category: str
    entry_point: str
    description: str = ""
    requires_config: tuple[str, ...] = ()
    path: Path | None = None


def discover(category: str) -> dict[str, PluginManifest]:
    """Varre plugins/<category>/*/plugin.yaml e retorna um dict name -> manifest."""
    category_dir = PLUGINS_ROOT / category
    manifests: dict[str, PluginManifest] = {}
    if not category_dir.is_dir():
        return manifests

    for plugin_dir in sorted(category_dir.iterdir()):
        manifest_file = plugin_dir / "plugin.yaml"
        if not plugin_dir.is_dir() or not manifest_file.exists():
            continue
        raw = yaml.safe_load(manifest_file.read_text(encoding="utf-8")) or {}
        try:
            manifest = PluginManifest(
                name=raw["name"],
                category=raw.get("category", category),
                entry_point=raw["entry_point"],
                description=raw.get("description", ""),
                requires_config=tuple(raw.get("requires_config", [])),
                path=plugin_dir,
            )
        except KeyError as exc:
            raise PluginLoadError(f"plugin.yaml inválido em {manifest_file}: falta {exc}") from exc
        manifests[manifest.name] = manifest
    return manifests


def discover_all() -> dict[str, dict[str, PluginManifest]]:
    """Descobre plugins em todas as categorias conhecidas. Útil para /plugins e docs."""
    categories = ["sources", "ai", "notifications", "reports", "exports"]
    return {category: discover(category) for category in categories}


def _import_entry_point(entry_point: str) -> type:
    module_path, _, class_name = entry_point.partition(":")
    if not module_path or not class_name:
        raise PluginLoadError(
            f"entry_point inválido: '{entry_point}' (esperado 'modulo:Classe')"
        )
    repo_root = str(PLUGINS_ROOT.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        raise PluginLoadError(f"falha ao importar '{entry_point}': {exc}") from exc


def load_plugin(category: str, name: str, config: dict[str, Any] | None = None) -> Any:
    """Descobre, importa, instancia e inicializa um único plugin pelo nome."""
    manifests = discover(category)
    if name not in manifests:
        available = ", ".join(sorted(manifests)) or "(nenhum)"
        raise PluginNotFoundError(
            f"Plugin '{name}' não encontrado em plugins/{category}/. Disponíveis: {available}"
        )
    manifest = manifests[name]
    config = config or {}
    missing = [key for key in manifest.requires_config if not config.get(key)]
    if missing:
        raise PluginLoadError(
            f"Plugin '{name}' requer config ausente: {missing} (ver plugin.yaml:requires_config)"
        )

    plugin_class = _import_entry_point(manifest.entry_point)
    instance = plugin_class()
    instance.initialize(config)
    logger.info("plugin_loaded", category=category, name=name)
    return instance


def load_enabled(
    category: str,
    enabled_names: list[str],
    config: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Carrega todos os plugins habilitados de uma categoria (config por nome de plugin, opcional)."""
    config = config or {}
    loaded: dict[str, Any] = {}
    for name in enabled_names:
        loaded[name] = load_plugin(category, name, config.get(name))
    return loaded
