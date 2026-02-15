"""山西地电用电查询 - 配置流程"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api import SxgjdlApiClient, SxgjdlApiError
from .const import (
    DOMAIN,
    CONF_CONS_NO,
    CONF_ORG_NO,
    CONF_OPEN_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONS_NO): cv.string,
        vol.Required(CONF_ORG_NO): cv.string,
        vol.Optional(CONF_OPEN_ID, default=""): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=1440)
        ),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=1440)
        ),
    }
)


class SxgjdlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """配置流程：引导用户填写户号和组织编号"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            cons_no = user_input[CONF_CONS_NO].strip()
            org_no = user_input[CONF_ORG_NO].strip()
            open_id = user_input.get(CONF_OPEN_ID, "").strip()

            # 检查是否已添加相同户号
            await self.async_set_unique_id(cons_no)
            self._abort_if_unique_id_configured()

            # 验证户号是否有效
            client = SxgjdlApiClient(cons_no=cons_no, org_no=org_no, open_id=open_id)
            try:
                valid = await client.validate_connection()
                if not valid:
                    errors["base"] = "invalid_cons_no"
                else:
                    # 获取户名作为条目标题
                    cons_info = await client.get_cons_info()
                    cons_name = ""
                    if cons_info.get("flag"):
                        cons_name = (cons_info.get("data") or {}).get("consName", "")

                    title = f"山西地电 - {cons_name or cons_no}"
                    return self.async_create_entry(
                        title=title,
                        data={
                            CONF_CONS_NO: cons_no,
                            CONF_ORG_NO: org_no,
                            CONF_OPEN_ID: open_id,
                            CONF_SCAN_INTERVAL: user_input.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        },
                    )
            except SxgjdlApiError:
                errors["base"] = "cannot_connect"
            finally:
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SxgjdlOptionsFlow(config_entry)


class SxgjdlOptionsFlow(config_entries.OptionsFlow):
    """选项流程：允许修改刷新间隔"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=1440)),
                }
            ),
        )
