"""山西地电用电查询 - 传感器实体"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_CONS_NO
from .coordinator import SxgjdlDataCoordinator

_LOGGER = logging.getLogger(__name__)

UNIT_YUAN = "元"
UNIT_KWH = UnitOfEnergy.KILO_WATT_HOUR


@dataclass(frozen=True)
class SxgjdlSensorEntityDescription(SensorEntityDescription):
    """扩展传感器描述"""
    data_key: str = ""
    extra_attrs_keys: list = field(default_factory=list)


SENSOR_DESCRIPTIONS: tuple[SxgjdlSensorEntityDescription, ...] = (
    # ---- 财务类（不用 MONETARY，该 device_class 要求 ISO 货币代码）----
    SxgjdlSensorEntityDescription(
        key="prepay_bal",
        data_key="prepay_bal",
        name="预付余额",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:cash",
    ),
    SxgjdlSensorEntityDescription(
        key="rcv_amt_total",
        data_key="rcv_amt_total",
        name="应收电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:cash-clock",
    ),
    SxgjdlSensorEntityDescription(
        key="unit_price",
        data_key="unit_price",
        name="当前电价",
        native_unit_of_measurement="元/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:currency-cny",
        extra_attrs_keys=["price_name"],
    ),
    # ---- 今日 ----
    SxgjdlSensorEntityDescription(
        key="today_usage",
        data_key="today_usage",
        name="今日用电量",
        native_unit_of_measurement=UNIT_KWH,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    SxgjdlSensorEntityDescription(
        key="today_amt",
        data_key="today_amt",
        name="今日预估电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:cash-fast",
    ),
    # ---- 本月 ----
    SxgjdlSensorEntityDescription(
        key="month_usage",
        data_key="month_usage",
        name="本月用电量",
        native_unit_of_measurement=UNIT_KWH,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:calendar-month",
    ),
    SxgjdlSensorEntityDescription(
        key="month_amt",
        data_key="month_amt",
        name="本月已结电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:receipt",
    ),
    SxgjdlSensorEntityDescription(
        key="month_esti_usage",
        data_key="month_esti_usage",
        name="本月预估用电量",
        native_unit_of_measurement=UNIT_KWH,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chart-line",
    ),
    SxgjdlSensorEntityDescription(
        key="month_esti_amt",
        data_key="month_esti_amt",
        name="本月预估电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chart-areaspline",
    ),
    # ---- 上月 ----
    SxgjdlSensorEntityDescription(
        key="last_month_usage",
        data_key="last_month_usage",
        name="上月用电量",
        native_unit_of_measurement=UNIT_KWH,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:history",
    ),
    SxgjdlSensorEntityDescription(
        key="last_month_amt",
        data_key="last_month_amt",
        name="上月电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:receipt-text",
    ),
    # ---- 年度 ----
    SxgjdlSensorEntityDescription(
        key="year_total_usage",
        data_key="year_total_usage",
        name="本年用电量",
        native_unit_of_measurement=UNIT_KWH,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:calendar-year",
    ),
    SxgjdlSensorEntityDescription(
        key="year_total_amt",
        data_key="year_total_amt",
        name="本年电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:finance",
    ),
    # ---- 最新账单 ----
    SxgjdlSensorEntityDescription(
        key="latest_bill_amt",
        data_key="latest_bill_amt",
        name="最近一期账单电费",
        native_unit_of_measurement=UNIT_YUAN,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:file-document-outline",
        extra_attrs_keys=["latest_bill_ym", "latest_bill_pq"],
    ),
    SxgjdlSensorEntityDescription(
        key="latest_bill_pq",
        data_key="latest_bill_pq",
        name="最近一期账单用电量",
        native_unit_of_measurement=UNIT_KWH,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:file-chart-outline",
        extra_attrs_keys=["latest_bill_ym"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """注册传感器实体"""
    coordinator: SxgjdlDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    cons_no = entry.data[CONF_CONS_NO]

    entities = [
        SxgjdlSensor(coordinator, description, cons_no, entry)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class SxgjdlSensor(CoordinatorEntity[SxgjdlDataCoordinator], SensorEntity):
    """山西地电传感器实体"""

    entity_description: SxgjdlSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SxgjdlDataCoordinator,
        description: SxgjdlSensorEntityDescription,
        cons_no: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._cons_no = cons_no
        self._entry = entry
        self._attr_unique_id = f"{cons_no}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        data = self.coordinator.data or {}
        cons_name = data.get("cons_name", self._cons_no)
        elec_addr = data.get("elec_addr", "")
        return DeviceInfo(
            identifiers={(DOMAIN, self._cons_no)},
            name=f"山西地电 - {cons_name}",
            manufacturer="山西省地方电力（集团）有限公司",
            model=f"户号: {self._cons_no}",
            sw_version="1.0.0",
            configuration_url="http://ddwxyw.sxgjdl.com",
            suggested_area=elec_addr or "电力",
        )

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        data = self.coordinator.data or {}

        for k in self.entity_description.extra_attrs_keys:
            if k in data:
                attrs[k] = data[k]

        if "cons_name" in data:
            attrs["户名"] = data["cons_name"]
        if "elec_addr" in data:
            attrs["用电地址"] = data["elec_addr"]
        if "org_name" in data:
            attrs["供电所"] = data["org_name"]
        if "last_mr_date" in data:
            attrs["上次抄表日期"] = data["last_mr_date"]

        return attrs
