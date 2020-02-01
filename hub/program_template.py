import hub
from runtime import VirtualMachine

# When program starts
async def on_start(vm, stack):
  for i in range(11):
    # Set LED color
    hub.led(i)
    # Sleep 1 second
    yield 1000

def setup(rpc, system):
  vm = VirtualMachine(rpc, system, "")
  vm.register_on_start("", on_start)
  return vm
