# Copyright 2022 University of Chicago
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ironic_lib import utils
from ironic_python_agent import hardware
from oslo_log import log

LOG = log.getLogger()


SUPPORTED_SYSTEMS = [
    {"system_manufacturer": "FUJITSU", "system_product_name": "FX700"},
]

# All the helper methods should be kept outside of the HardwareManager
# so they'll never get accidentally called by dispatch_to_managers()


def _detect_hardware():
    """Detect if system is Fugaku Node."""
    system_manufacturer = utils.execute("dmidecode -s system-manufacturer")
    system_product_name = utils.execute("dmidecode -s system-product-name")

    system_info = {
        "system_manufacturer": system_manufacturer,
        "system_product_name": system_product_name,
    }
    LOG.debug(f"system info: {system_info}")

    if system_info in SUPPORTED_SYSTEMS:
        return True
    else:
        return False


class FugakuNodeHardwareManager(hardware.HardwareManager):
    """Hardware manager to support TACC Fugaku nodes"""

    # All hardware managers have a name and a version.
    # Version should be bumped anytime a change is introduced. This will
    # signal to Ironic that if automatic node cleaning is in progress to
    # restart it from the beginning, to ensure consistency. The value can
    # be anything; it's checked for equality against previously seen
    # name:manager pairs.
    HARDWARE_MANAGER_NAME = "FugakuNodeHardwareManager"
    HARDWARE_MANAGER_VERSION = "1"

    def evaluate_hardware_support(self):
        """Declare level of hardware support provided.

        Since this example covers a case of supporting a specific device,
        this method is where you would do anything needed to initalize that
        device, including loading drivers, and then detect if one exists.

        In some cases, if you expect the hardware to be available on any node
        running this hardware manager, or it's undetectable, you may want to
        return a static value here.

        Be aware all managers' loaded in IPA will run this method before IPA
        performs a lookup or begins heartbeating, so the time needed to
        execute this method will make cleaning and deploying slower.

        :returns: HardwareSupport level for this manager.
        """
        if _detect_hardware():
            # This actually resolves down to an int. Upstream IPA will never
            # return a value higher than 2 (HardwareSupport.MAINLINE). This
            # means your managers should always be SERVICE_PROVIDER or higher.
            LOG.debug("Found example device, returning SERVICE_PROVIDER")
            return hardware.HardwareSupport.SERVICE_PROVIDER
        else:
            # If the hardware isn't supported, return HardwareSupport.NONE (0)
            # in order to prevent IPA from loading its clean steps or
            # attempting to use any methods inside it.
            LOG.debug("No example devices found, returning NONE")
            return hardware.HardwareSupport.NONE

    def list_hardware_info(self):
        """Override list_hardware_info due to IPMI limitations"""

        start = time.time()
        LOG.info("Collecting full inventory")
        hardware_info = {}
        hardware_info["interfaces"] = self.list_network_interfaces()
        hardware_info["cpu"] = self.get_cpus()
        hardware_info["disks"] = self.list_block_devices()
        hardware_info["memory"] = self.get_memory()
        hardware_info["system_vendor"] = self.get_system_vendor_info()
        hardware_info["boot"] = self.get_boot_info()
        hardware_info["hostname"] = netutils.get_hostname()

        ## These methods are disabled for the Fugaku nodes, as they ONLY
        ## support power on/off/status via IPMI.

        # hardware_info["bmc_address"] = self.get_bmc_address()
        # hardware_info["bmc_v6address"] = self.get_bmc_v6address()
        # hardware_info["bmc_mac"] = self.get_bmc_mac()

        LOG.info("Inventory collected in %.2f second(s)", time.time() - start)
        return hardware_info
