"""Pylontech (high voltage) BMS sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_COORDINATOR
from .coordinator import PylontechUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    "A": SensorEntityDescription(
        key="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
    ),
    "V": SensorEntityDescription(
        key="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    "Ah": SensorEntityDescription(
        key="Ah",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    "Wh": SensorEntityDescription(
        key="Wh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    "C": SensorEntityDescription(
        key="C",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    "%": SensorEntityDescription(
        key="%",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    " ": SensorEntityDescription(
        key="text",
    ),
}
DIAG_SENSOR = SensorEntityDescription(
    key="_",
    state_class=SensorStateClass.MEASUREMENT,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor entities from a config entry."""
    coordinator: PylontechUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        KEY_COORDINATOR
    ]

    entities: list[PylontectSensorEntity] = []

    # Core BMS sensors
    entities.extend(
        PylontectSensorEntity(coordinator, sensor_id, sensor.name, sensor.unit, None)
        for sensor_id, sensor in coordinator.sensors.items()
    )
    # Battery units sensors
    for bmu in range(len(coordinator.unit_device_infos)):
        entities.extend(
            PylontectSensorEntity(
                coordinator,
                f"{sensor_id}_bmu_{bmu}",
                f"{sensor.name} (bmu {bmu})",
                sensor.unit,
                bmu,
            )
            for sensor_id, sensor in coordinator.unit_sensors.items()
        )

    async_add_entities(entities)


class PylontectSensorEntity(
    CoordinatorEntity[PylontechUpdateCoordinator], SensorEntity
):
    """Representation of an Electric Vehicle Charger status device."""

    def __init__(
        self,
        coordinator: PylontechUpdateCoordinator,
        sensor_id: str,
        name: str,
        unit: str,
        bmu: int,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{sensor_id}-{coordinator.serial_nr}"
        self._attr_device_info = (
            coordinator.unit_device_infos[bmu]
            if bmu is not None
            else coordinator.device_info
        )
        self.entity_description = _DESCRIPTIONS.get(unit, DIAG_SENSOR)
        self._sensor_id = sensor_id

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        return self.coordinator.sensor_value(self._sensor_id)
