#!/usr/bin/env python3
import logging
from typing import Iterable

from modules.common import modbus
from modules.common.abstract_device import DeviceDescriptor
from modules.common.component_context import SingleComponentUpdateContext
from modules.common.configurable_device import ComponentFactoryByType, ConfigurableDevice, MultiComponentUpdater
from modules.devices.sma.sma_sunny_island.bat import SunnyIslandBat
from modules.devices.sma.sma_sunny_island.config import SmaSunnyIsland, SmaSunnyIslandBatSetup

log = logging.getLogger(__name__)


def create_device(device_config: SmaSunnyIsland):
    client = None

    def create_bat_component(component_config: SmaSunnyIslandBatSetup):
        nonlocal client
        return SunnyIslandBat(component_config, client=client)

    def update_components(components: Iterable[SunnyIslandBat]):
        nonlocal client
        with client:
            for component in components:
                with SingleComponentUpdateContext(component.fault_state):
                    component.update()

    def initializer():
        nonlocal client
        client = modbus.ModbusTcpClient_(device_config.configuration.ip_address, device_config.configuration.port)

    return ConfigurableDevice(
        device_config=device_config,
        initializer=initializer,
        component_factory=ComponentFactoryByType(
            bat=create_bat_component,
        ),
        component_updater=MultiComponentUpdater(update_components)
    )


device_descriptor = DeviceDescriptor(configuration_factory=SmaSunnyIsland)
