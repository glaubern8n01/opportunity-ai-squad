"""Exceções de domínio compartilhadas por core, agents e plugins."""

from __future__ import annotations


class OpportunitySquadError(Exception):
    """Exceção base de todo o sistema."""


class ConfigurationError(OpportunitySquadError):
    """Variável de ambiente ou configuração obrigatória ausente/inválida."""


class PluginError(OpportunitySquadError):
    """Erro genérico de plugin (fonte, IA, notificação ou relatório)."""


class PluginNotFoundError(PluginError):
    """Plugin habilitado na configuração não foi encontrado no registry."""


class PluginLoadError(PluginError):
    """Plugin encontrado mas falhou ao carregar/inicializar."""


class SourceFetchError(PluginError):
    """Falha ao buscar dados em uma fonte externa (após esgotar retries)."""


class AIProviderError(PluginError):
    """Falha ao chamar o provedor de IA."""


class NotificationError(PluginError):
    """Falha ao enviar notificação."""
