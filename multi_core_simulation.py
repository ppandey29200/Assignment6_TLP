import m5
from m5.objects import *
import threading

# DAXPY kernel: Y = a * X + Y
def daxpy(a, X, Y, start, end):
    for i in range(start, end):
        Y[i] = a * X[i] + Y[i]

def multi_threaded_daxpy(a, X, Y, num_threads):
    threads = []
    n = len(X)
    chunk_size = n // num_threads

    for i in range(num_threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i != num_threads - 1 else n
        thread = threading.Thread(target=daxpy, args=(a, X, Y, start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

class MySystem(System):
    def __init__(self, num_cores, opLat, issueLat):
        super(MySystem, self).__init__()
        self.clk_domain = SrcClockDomain()
        self.clk_domain.clock = '1GHz'
        self.clk_domain.voltage_domain = VoltageDomain()

        self.mem_mode = 'timing'
        self.mem_ranges = [AddrRange('512MB')]

        # Instantiate multiple CPU cores
        self.cpu = [TimingSimpleCPU(cpu_id=i) for i in range(num_cores)]

        # Create the memory bus
        self.membus = SystemXBar()

        # Connect the CPUs to the membus
        for cpu in self.cpu:
            cpu.icache_port = self.membus.cpu_side_ports
            cpu.dcache_port = self.membus.cpu_side_ports

        # Create a memory controller
        self.mem_ctrl = DDR3_1600_8x8()
        self.mem_ctrl.range = self.mem_ranges[0]
        self.mem_ctrl.port = self.membus.mem_side_ports

        # Connect the system port to the membus
        self.system_port = self.membus.cpu_side_ports

        # Define the functional unit pool with the specified opLat and issueLat
        self.fu_pool = FUPool(funcUnits=[
            FunctionalUnit(opLat=opLat, issueLat=issueLat, count=1, opList=[
                OpDesc(opClass='FloatAdd', opLat=opLat),
                OpDesc(opClass='FloatCmp', opLat=opLat),
                OpDesc(opClass='FloatCvt', opLat=opLat),
                OpDesc(opClass='FloatDiv', opLat=opLat),
                OpDesc(opClass='FloatMult', opLat=opLat),
                OpDesc(opClass='FloatMisc', opLat=opLat),
                OpDesc(opClass='FloatSqrt', opLat=opLat),
                OpDesc(opClass='SimdAdd', opLat=opLat),
                OpDesc(opClass='SimdAddAcc', opLat=opLat),
                OpDesc(opClass='SimdAlu', opLat=opLat),
                OpDesc(opClass='SimdCmp', opLat=opLat),
                OpDesc(opClass='SimdCvt', opLat=opLat),
                OpDesc(opClass='SimdMisc', opLat=opLat),
                OpDesc(opClass='SimdMult', opLat=opLat),
                OpDesc(opClass='SimdMultAcc', opLat=opLat),
                OpDesc(opClass='SimdShift', opLat=opLat),
                OpDesc(opClass='SimdShiftAcc', opLat=opLat),
                OpDesc(opClass='SimdSqrt', opLat=opLat),
                OpDesc(opClass='SimdFloatAdd', opLat=opLat),
                OpDesc(opClass='SimdFloatAlu', opLat=opLat),
                OpDesc(opClass='SimdFloatCmp', opLat=opLat),
                OpDesc(opClass='SimdFloatCvt', opLat=opLat),
                OpDesc(opClass='SimdFloatDiv', opLat=opLat),
                OpDesc(opClass='SimdFloatMisc', opLat=opLat),
                OpDesc(opClass='SimdFloatMult', opLat=opLat),
                OpDesc(opClass='SimdFloatMultAcc', opLat=opLat),
                OpDesc(opClass='SimdFloatSqrt', opLat=opLat)
            ])
        ])

        # Define the workload
        binary = 'tests/test-progs/hello/bin/x86/linux/hello'
        self.workload = SEWorkload.init_compatible(binary)

        process = Process()
        process.cmd = [binary]
        for cpu in self.cpu:
            cpu.workload = process
            cpu.createThreads()

def run_simulation(num_cores, opLat, issueLat):
    print(f"Running simulation with opLat = {opLat}, issueLat = {issueLat}...")
    root = Root(full_system=False, system=MySystem(num_cores, opLat, issueLat))
    m5.instantiate()
    print("Beginning simulation!")
    exit_event = m5.simulate()
    print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))

    # Collect and print the results
    total_cycles = m5.curTick()
    floating_point_operations = 600000  # Example value, replace with actual calculation
    throughput = floating_point_operations / total_cycles

    print(f"Configuration: opLat = {opLat}, issueLat = {issueLat}")
    print(f"Total Cycles: {total_cycles} cycles")
    print(f"Floating-point Operations: {floating_point_operations} operations")
    print(f"Throughput: {throughput:.3f} operations per cycle")

if __name__ == '__main__':
    num_cores = 4  # Set the number of CPU cores

    # Run simulations with different configurations of opLat and issueLat
    configurations = [(1, 6), (2, 5), (3, 4)]
    for opLat, issueLat in configurations:
        run_simulation(num_cores, opLat, issueLat)