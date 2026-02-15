"""山西地电用电查询 - Home Assistant 集成"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import SxgjdlApiClient, SxgjdlApiError
from .const import (
    DOMAIN,
    CONF_CONS_NO,
    CONF_ORG_NO,
    CONF_OPEN_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .coordinator import SxgjdlDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """初始化集成"""
    cons_no = entry.data[CONF_CONS_NO]
    org_no = entry.data[CONF_ORG_NO]
    open_id = entry.data.get(CONF_OPEN_ID, "")
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    client = SxgjdlApiClient(cons_no=cons_no, org_no=org_no, open_id=open_id)

    # 验证连接
    try:
        valid = await client.validate_connection()
        if not valid:
            await client.close()
            raise ConfigEntryNotReady(f"户号 {cons_no} 验证失败，请检查配置")
    except SxgjdlApiError as err:
        await client.close()
        raise ConfigEntryNotReady(f"无法连接到山西地电服务器: {err}") from err

    coordinator = SxgjdlDataCoordinator(hass, client, scan_interval)

    # 首次刷新
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 监听选项变更（刷新间隔调整）
    entry.async_on_unload(entry.add_update_listener(_async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SxgjdlDataCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()
    return unload_ok


async def _async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """选项变更时重载集成"""
    await hass.config_entries.async_reload(entry.entry_id)
