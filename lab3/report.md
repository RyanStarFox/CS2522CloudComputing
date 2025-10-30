# 实验三: IO 虚拟化

<center>[523031910224] [邵言]</center>

## 1 调研部分

### 问题1： x86 中 MMIO 与 PIO 的概念（参考书籍的 4.2.2 节）

- PIO：I/O设备有独立的地址空间，访问需要用特定的指令（in/out)，速度一般较慢。
- MMIO：I/O设备与内存公用地址空间，直接使用普通读写指令访问，速度一般更快。

### 问题2：请调研设备枚举过程并根据你的理解回答设备是如何被发现的

1. UEFI（BIOS）阶段：开机后，扫描硬件，包括CPU、RAM、主板、PCI、ACPI表等等，把信息传输给OS。
2. OS内核阶段：继续枚举硬件

   1. 根据ACPI表解析设备树
   2. PCI/PCIe 总线扫描，读取Vendor ID / Device ID，如果不是0xFFFF表示有设备
   3. USB设备： 从 Root Hub 开始，逐层扫描 Port
   4. 其它设备：继续枚举
3. 设备被枚举出来之后，会：

   1. 设备匹配：根据 Vendor ID / Device ID / ACPI 名字匹配驱动
   2. 驱动加载：调用 probe() 进入驱动初始化
   3. 配置 BAR / IRQ / DMA，设置总线访问、内存映射、中断
   4. 创建设备节点：/dev/...，sysfs，udev rules 等 

## 2 实验目的

学习、了解虚拟机调用I/O设备的具体步骤和过程。

## 3 实验步骤

1. 根据指令启动虚拟机
2. 安装设备驱动
3. 查看PCI设备相关信息
4. 构造设备节点
5. 运行测试代码
6. 输出调试信息
7. 分析PCI设备信息与调试信息

## 4 实验分析

### 4.1 lspci

按照地址顺序（格式：PCI Bus Number:Device Number.Function Number）枚举了pci的设备，包括：

主桥、ISA桥、IDE控制器、ACPI控制器、显卡、网卡、未分类设备（edu_pci）、VirtIO块设备（虚拟硬盘）

其中VirtIO块设备是Virt前段设备，说明该系统使用了前后端分离的虚拟机系统。

### 4.2 lspci -s 00:04.0 -vvv -xxxx

枚举了00:04.0位置设备，也就是edu_pci的相关信息

- 使用了MMIO，映射到0xfea00000，大小32bit，也就是1MB
- 没有启用总线主控（不能主动发起DMA）
- Status: Caps+: 支持PCI功能拓展
- 还有一些其他的标志
- INTA#中断信号被影射到IRQ 10
- 那个使用edu_pci驱动管理该设备
- 它对应的PCI配置空间的原始内容
  - VendorID：0x1234
  - DeviceID：e811
  - BAR0：0xfea00000
  - 其他信息

### 4.3 注册了pci_edu的信息

```shell
ubuntu@ubuntu:~/Book/Chapter4$ ls /dev/edu

ubuntu@ubuntu:~/Book/Chapter4$ sudo mknod /dev/edu c 245 0

ubuntu@ubuntu:~/Book/Chapter4$ ls /dev/edu
/dev/edu
```

注册pci_edu之前，/dev/edu不存在，因此无输出。使用mknod指令注册io，访问/dev/edu有输出

### 4.4 模拟调用一次IO

```shell
ubuntu@ubuntu:~/Book/Chapter4$ sudo dmesg --clear
ubuntu@ubuntu:~/Book/Chapter4$ sudo ./test
ubuntu@ubuntu:~/Book/Chapter4$ sudo dmesg
[  155.593863] length 100000
...
```

./test依次触发了

1. 传入参数，驱动把参数存在了设备的MMIO寄存器（BAR0）
2. 设备执行操作，将结果写回MMIO区域
3. 完成计算后，通过IRQ10向OS发送中断信号

## 5 遇到的问题及解决方案

开始时直接运行`start.sh`启动虚拟机，发现实验结果与预期不符。之后改用实验指导上的指令启动L2虚拟机，实验结果符合预期。

```shell
sudo qemu-system-x86_64  -smp 1 -m 2G -enable-kvm \
    -drive file=./ubuntu18.qcow2,if=virtio \
    -drive file=seed.iso,if=virtio \
    -device edu,dma_mask=0xFFFFFFFF \
    -net nic \
    -net user,hostfwd=tcp::2222-:22 \
    -nographic
```

## 附录

### L2虚拟机输出

```shell
ubuntu@ubuntu:~/Book/Chapter4$ lspci
00:00.0 Host bridge: Intel Corporation 440FX - 82441FX PMC [Natoma] (rev 02)
00:01.0 ISA bridge: Intel Corporation 82371SB PIIX3 ISA [Natoma/Triton II]
00:01.1 IDE interface: Intel Corporation 82371SB PIIX3 IDE [Natoma/Triton II]
00:01.3 Bridge: Intel Corporation 82371AB/EB/MB PIIX4 ACPI (rev 03)
00:02.0 VGA compatible controller: Device 1234:1111 (rev 02)
00:03.0 Ethernet controller: Intel Corporation 82540EM Gigabit Ethernet Control)
00:04.0 Unclassified device [00ff]: Device 1234:11e8 (rev 10)
00:05.0 SCSI storage controller: Red Hat, Inc. Virtio block device
00:06.0 SCSI storage controller: Red Hat, Inc. Virtio block device

ubuntu@ubuntu:~/Book/Chapter4$ lspci -s 00:04.0 -vvv -xxxx
00:04.0 Unclassified device [00ff]: Device 1234:11e8 (rev 10)
        Subsystem: Red Hat, Inc. Device 1100
        Physical Slot: 4
        Control: I/O+ Mem+ BusMaster- SpecCycle- MemWINV- VGASnoop- ParErr- Ste-
        Status: Cap+ 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort--
        Interrupt: pin A routed to IRQ 10
        Region 0: Memory at fea00000 (32-bit, non-prefetchable) [size=1M]
        Capabilities: <access denied>
        Kernel driver in use: edu_pci
00: 34 12 e8 11 03 01 10 00 10 00 ff 00 00 00 00 00
10: 00 00 a0 fe 00 00 00 00 00 00 00 00 00 00 00 00
20: 00 00 00 00 00 00 00 00 00 00 00 00 f4 1a 00 11
30: 00 00 00 00 40 00 00 00 00 00 00 00 0b 01 00 00

ubuntu@ubuntu:~/Book/Chapter4$ cat /proc/devices | grep edu

ubuntu@ubuntu:~/Book/Chapter4$ ls /dev/edu

ubuntu@ubuntu:~/Book/Chapter4$ sudo dmesg
[  358.696204] length 100000
[  358.696273] config 0 34
[  358.696310] config 1 12
[  358.696347] config 2 e8
[  358.696383] config 3 11
[  358.696419] config 4 3
[  358.696454] config 5 1
[  358.696490] config 6 10
[  358.696526] config 7 0
[  358.696563] config 8 10
[  358.696599] config 9 0
[  358.696636] config a ff
[  358.696672] config b 0
[  358.696708] config c 0
[  358.696745] config d 0
[  358.696781] config e 0
[  358.696820] config f 0
[  358.696856] config 10 0
[  358.696893] config 11 0
[  358.696929] config 12 a0
[  358.696965] config 13 fe
[  358.697001] config 14 0
[  358.697038] config 15 0
[  358.697074] config 16 0
[  358.697114] config 17 0
[  358.697150] config 18 0
[  358.697186] config 19 0
[  358.697223] config 1a 0
[  358.697259] config 1b 0
[  358.697295] config 1c 0
[  358.697331] config 1d 0
[  358.697367] config 1e 0
[  358.697404] config 1f 0
[  358.697440] config 20 0
[  358.697476] config 21 0
[  358.697512] config 22 0
[  358.697549] config 23 0
[  358.697585] config 24 0
[  358.697620] config 25 0
[  358.697656] config 26 0
[  358.697692] config 27 0
[  358.697728] config 28 0
[  358.697765] config 29 0
[  358.697801] config 2a 0
[  358.697837] config 2b 0
[  358.697874] config 2c f4
[  358.697910] config 2d 1a
[  358.697946] config 2e 0
[  358.697982] config 2f 11
[  358.698019] config 30 0
[  358.698053] config 31 0
[  358.698093] config 32 0
[  358.698129] config 33 0
[  358.698165] config 34 40
[  358.698200] config 35 0
[  358.698236] config 36 0
[  358.698272] config 37 0
[  358.698308] config 38 0
[  358.698344] config 39 0
[  358.698381] config 3a 0
[  358.698417] config 3b 0
[  358.698453] config 3c b
[  358.698489] config 3d 1
[  358.698526] config 3e 0
[  358.698563] config 3f 0
[  358.698563] dev->irq a
[  358.698594] io 0 10000ed
[  358.698615] io 4 0
[  358.698635] io 8 375f00
[  358.698655] io c ffffffff
[  358.698674] io 10 ffffffff
[  358.698695] io 14 ffffffff
[  358.698715] io 18 ffffffff
[  358.698734] io 1c ffffffff
[  358.698754] io 20 80
[  358.698774] io 24 0
[  358.698795] io 28 ffffffff
[  358.698816] io 2c ffffffff
[  358.698836] io 30 ffffffff
[  358.698856] io 34 ffffffff
[  358.698876] io 38 ffffffff
[  358.698896] io 3c ffffffff
[  358.698916] io 40 ffffffff
[  358.698936] io 44 ffffffff
[  358.698956] io 48 ffffffff
[  358.698977] io 4c ffffffff
[  358.698997] io 50 ffffffff
[  358.699017] io 54 ffffffff
[  358.699037] io 58 ffffffff
[  358.699056] io 5c ffffffff
[  358.699094] io 60 ffffffff
[  358.699114] io 64 ffffffff
[  358.699135] io 68 ffffffff
[  358.699155] io 6c ffffffff
[  358.699178] io 70 ffffffff
[  358.699199] io 74 ffffffff
[  358.699219] io 78 ffffffff
[  358.699240] io 7c ffffffff
[  358.699260] io 80 a00104
[  358.699281] io 84 ffffffff
[  358.699301] io 88 40000
[  358.699322] io 8c ffffffff
[  358.699343] io 90 4
[  358.699363] io 94 ffffffff
[  358.699412] irq_handler irq = 10 dev = 245 irq_status = 12345678
[  359.712233] receive a FACTORIAL interrupter!
[  359.712234] irq_handler irq = 10 dev = 245 irq_status = 1
[  360.736462] computing result 375f00
[  360.836521] receive a DMA read interrupter!
[  360.836523] irq_handler irq = 10 dev = 245 irq_status = 100
[  362.860579] receive a DMA read interrupter!
[  362.860581] irq_handler irq = 10 dev = 245 irq_status = 100
/dev/edu
245 pci_edu
```
