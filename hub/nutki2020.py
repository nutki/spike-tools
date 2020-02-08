from random import randint as r
import hub
from runtime import VirtualMachine
I=550
nutki=[0,403776,338368,462976,340288,135296,0,14760206,15018318,14760206,15018318,0,0]
def u(p,s):
  return memoryview([b'2345623456', b'2567899999',b'0000023456',b'8889988899'][p])[s:]
def t(v, m=5, n=5):
  return 0 if v < 0 else n if v > m else v
async def on_start(vm, stack):
  for i in range(I*12):
    x = r(0, 4)
    y = r(0, 4)
    p = i // I
    q = lambda l: (i%I)//(I//l)
    s = (nutki[p] >> (24-x*5-y)) & 1
    f = lambda: u(2, t(q(15)-x-y))
    g = lambda: u(s, t(q(9)))
    h = lambda: u(s+2, t(x+q(6)-3))
    v = lambda: u(s+2, t(x+2))
    hub.display.pixel(y,x,[f,g,g,g,g,g,h,v,v,v,v,v,v][p]()[r(0,4)]-48)
    yield 1
  hub.display.clear()

def setup(rpc, system):
  vm = VirtualMachine(rpc, system, "Nutki2020")
  vm.register_on_start("on_start", on_start)
  return vm
