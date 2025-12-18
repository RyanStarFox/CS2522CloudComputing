#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验数据可视化脚本
根据 experiment.md 文件绘制性能对比图表
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import rcParams, font_manager
import platform

# 设置中文字体 - macOS专用优化
def setup_chinese_font():
    """设置中文字体 - 针对macOS优化"""
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
    
    system = platform.system()
    chinese_font_prop = None
    
    if system == 'Darwin':  # macOS
        # macOS上常见的中文字体路径（按优先级）
        mac_font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Supplemental/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
        ]
        
        # 尝试直接使用字体文件路径
        for font_path in mac_font_paths:
            if os.path.exists(font_path):
                try:
                    chinese_font_prop = font_manager.FontProperties(fname=font_path)
                    print(f"✓ 找到中文字体文件: {font_path}")
                    break
                except Exception as e:
                    continue
        
        # 如果直接路径失败，尝试从字体列表查找
        if chinese_font_prop is None:
            available_fonts = [f.name for f in font_manager.fontManager.ttflist]
            mac_chinese_fonts = ['PingFang SC', 'PingFang TC', 'STHeiti', 'Arial Unicode MS', 
                                'Hiragino Sans GB', 'Songti SC', 'Kaiti SC']
            
            for font_name in mac_chinese_fonts:
                if font_name in available_fonts:
                    try:
                        chinese_font_prop = font_manager.FontProperties(family=font_name)
                        print(f"✓ 使用中文字体: {font_name}")
                        break
                    except:
                        continue
        
        # 设置全局字体参数
        if chinese_font_prop:
            font_name = chinese_font_prop.get_name()
            rcParams['font.family'] = 'sans-serif'
            # 将中文字体放在最前面，确保优先使用
            rcParams['font.sans-serif'] = [font_name, 'PingFang SC', 'STHeiti', 
                                          'Arial Unicode MS', 'Hiragino Sans GB', 'DejaVu Sans']
        else:
            # 如果还是找不到，使用默认设置
            rcParams['font.family'] = 'sans-serif'
            rcParams['font.sans-serif'] = ['PingFang SC', 'STHeiti', 'Arial Unicode MS', 'DejaVu Sans']
            print("⚠ 使用默认中文字体设置")
            # 创建一个默认的字体属性对象
            chinese_font_prop = font_manager.FontProperties(family='PingFang SC')
    
    elif system == 'Windows':
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'SimSun']
        chinese_font_prop = font_manager.FontProperties(family='Microsoft YaHei')
        print("✓ 使用中文字体: Microsoft YaHei")
    else:  # Linux
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 
                                       'Noto Sans CJK SC', 'Source Han Sans CN']
        chinese_font_prop = font_manager.FontProperties(family='WenQuanYi Micro Hei')
        print("✓ 使用中文字体: WenQuanYi Micro Hei")
    
    # 确保负号正常显示
    rcParams['axes.unicode_minus'] = False
    
    return chinese_font_prop

# 初始化字体设置并获取字体属性对象
CHINESE_FONT = setup_chinese_font()

# 设置图表样式
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        pass

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'images')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==================== 数据定义 ====================

# 1. 启动时间数据
qemu_boot_data = {
    'kernel': [0.919, 0.926, 0.895, 0.893, 0.895, 0.887, 0.968, 0.926, 0.996, 1.019],
    'initrd': [1.40, 1.316, 1.302, 1.276, 1.294, 1.281, 1.375, 1.363, 1.401, 1.430],
    'userspace': [5.242, 5.273, 5.275, 5.282, 5.201, 5.290, 5.273, 5.253, 5.212, 4.976],
    'target': [1.931, 1.722, 1.728, 1.729, 1.734, 1.766, 1.789, 1.776, 1.800, 1.799]
}

stratovirt_boot_data = {
    'kernel': [0.647, 0.637, 0.650, 0.640, 0.649, 0.677, 0.658, 0.654, 0.653, 0.641],
    'userspace': [3.636, 3.611, 3.640, 3.594, 3.602, 3.605, 3.624, 3.635, 3.662, 3.593],
    'target': [1.793, 4.249, 1.809, 1.772, 1.767, 1.773, 1.815, 1.781, 1.804, 1.776]
}

# 2. 内存占用数据
qemu_memory_data = {
    'Kbytes': [1824384, 1803908, 1803908, 1803908, 1803908, 1803908, 1803908, 1803908, 1803908, 1803908],
    'RSS': [495252, 624560, 632876, 632908, 632956, 686228, 686260, 690432, 805068, 811116],
    'Dirty': [473928, 603108, 611424, 611456, 611504, 664776, 664808, 668980, 783688, 789420]
}

stratovirt_memory_data = {
    'Kbytes': [1128048] * 10,
    'RSS': [127672, 127820, 127580, 127864, 127648, 127904, 127604, 126748, 127388, 126480],
    'Dirty': [121824, 121848, 121724, 121892, 121676, 121968, 121768, 120892, 121528, 120672]
}

# 3. CPU性能数据
qemu_cpu_data = {
    'threads': [1, 1, 4, 4, 16, 16, 32, 32, 64, 64],
    'latency': [0.99, 0.85, 3.75, 3.87, 13.49, 13.70, 31.43, 31.29, 65.81, 62.08],
    'events_per_sec': [5061, 5884, 5313, 5155, 5894, 5813, 5052, 5079, 4827, 5119]
}

stratovirt_cpu_data = {
    'threads': [1, 1, 4, 4, 16, 16, 32, 32, 64, 64],
    'latency': [0.80, 0.80, 3.15, 3.17, 12.14, 12.25, 23.92, 23.67, 49.36, 46.17],
    'events_per_sec': [1252, 1255, 1256, 1250, 1269, 1271, 1261, 1269, 1145, 1233]
}

# 4. 内存性能数据
qemu_mem_perf_data = {
    '1k': {'Seq': [1832904, 1826665], 'Rnd': [1078962, 1090551]},
    '2k': {'Seq': [1657231, 1654971], 'Rnd': [703565, 757692]},
    '4k': {'Seq': [1456968, 1429842], 'Rnd': [465320, 453210]},
    '8k': {'Seq': [1152278, 1139605], 'Rnd': [259044, 268518]}
}

stratovirt_mem_perf_data = {
    '1k': {'Seq': [2197550, 2086536], 'Rnd': [1241593, 1250813]},
    '2k': {'Seq': [1998896, 1920943], 'Rnd': [807468, 810719]},
    '4k': {'Seq': [1639204, 1629454], 'Rnd': [484260, 484382]},
    '8k': {'Seq': [1246568, 1252054], 'Rnd': [269157, 257956]}
}

# 5. I/O性能数据
qemu_io_data = {
    'config1': {
        'seqwr': {'written': [25.15, 24.78]},
        'seqrd': {'read': [303.08, 317.37]},
        'rndwr': {'written': [8.10, 8.46]},
        'rndrd': {'read': [12.79, 12.60]}
    },
    'config2': {
        'seqwr': {'written': [305.60, 313.25]},
        'seqrd': {'read': [376.65, 360.86]},
        'rndwr': {'written': [322.58, 332.44]},
        'rndrd': {'read': [368.63, 360.22]}
    },
    'config3': {
        'seqwr': {'written': [314.04, 318.14]},
        'seqrd': {'read': [315.27, 241.18]},
        'rndwr': {'written': [338.57, 336.82]},
        'rndrd': {'read': [337.01, 331.89]}
    }
}

stratovirt_io_data = {
    'config1': {
        'seqwr': {'written': [17.89, 17.74]},
        'seqrd': {'read': [3249.85, 3293.29]},
        'rndwr': {'written': [33.44, 31.69]},
        'rndrd': {'read': [2841.18, 2849.71]}
    },
    'config2': {
        'seqwr': {'written': [794.03, 761.76]},
        'seqrd': {'read': [7776.59, 7821.15]},
        'rndwr': {'written': [650.38, 636.89]},
        'rndrd': {'read': [7548.34, 7513.79]}
    },
    'config3': {
        'seqwr': {'written': [294.43, 297.41]},
        'seqrd': {'read': [3115.00, 3316.26]},
        'rndwr': {'written': [99.62, 98.18]},
        'rndrd': {'read': [2750.20, 2753.07]}
    }
}

# ==================== 辅助函数 ====================

def calculate_mean(data_list):
    """计算平均值"""
    return np.mean(data_list)

def calculate_mean_dict(data_dict):
    """计算字典中每个列表的平均值"""
    return {key: calculate_mean(values) for key, values in data_dict.items()}

# ==================== 图表绘制函数 ====================

def plot_boot_time():
    """1. 启动时间条形图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 计算平均值
    qemu_avg = calculate_mean_dict(qemu_boot_data)
    stratovirt_avg = calculate_mean_dict(stratovirt_boot_data)
    
    # 准备数据
    categories = ['Kernel', 'Userspace', 'Target Reached']
    qemu_values = [qemu_avg['kernel'], qemu_avg['userspace'], qemu_avg['target']]
    stratovirt_values = [stratovirt_avg['kernel'], stratovirt_avg['userspace'], stratovirt_avg['target']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, qemu_values, width, label='QEMU', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, stratovirt_values, width, label='StratoVirt', color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('阶段', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_ylabel('时间 (秒)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_title('启动时间对比', fontsize=14, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(prop=CHINESE_FONT)
    ax.grid(axis='y', alpha=0.3)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'boot_time_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 启动时间对比图已保存: {output_path}")
    plt.close()

def plot_memory_usage():
    """2. 内存占用堆叠条形图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 计算平均值
    qemu_avg = calculate_mean_dict(qemu_memory_data)
    stratovirt_avg = calculate_mean_dict(stratovirt_memory_data)
    
    # 转换为MB
    qemu_mb = {k: v/1024 for k, v in qemu_avg.items()}
    stratovirt_mb = {k: v/1024 for k, v in stratovirt_avg.items()}
    
    platforms = ['QEMU', 'StratoVirt']
    kbytes = [qemu_mb['Kbytes'], stratovirt_mb['Kbytes']]
    rss = [qemu_mb['RSS'], stratovirt_mb['RSS']]
    dirty = [qemu_mb['Dirty'], stratovirt_mb['Dirty']]
    
    x = np.arange(len(platforms))
    width = 0.6
    
    bars1 = ax.bar(x, kbytes, width, label='Kbytes', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x, rss, width, bottom=kbytes, label='RSS', color='#2ecc71', alpha=0.8)
    bars3 = ax.bar(x, dirty, width, bottom=[k+r for k, r in zip(kbytes, rss)], 
                   label='Dirty', color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('虚拟化平台', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_ylabel('内存占用 (MB)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_title('内存占用对比（堆叠）', fontsize=14, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_xticks(x)
    ax.set_xticklabels(platforms)
    ax.legend(prop=CHINESE_FONT)
    ax.grid(axis='y', alpha=0.3)
    
    # 添加总数值标签
    totals = [k+r+d for k, r, d in zip(kbytes, rss, dirty)]
    for i, total in enumerate(totals):
        ax.text(i, total, f'{total:.0f} MB', ha='center', va='bottom', 
               fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'memory_usage_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 内存占用对比图已保存: {output_path}")
    plt.close()

def plot_cpu_performance():
    """3. CPU性能对比：Threads vs Latency"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 按线程数分组并计算平均延迟
    qemu_threads_dict = {}
    for t, l in zip(qemu_cpu_data['threads'], qemu_cpu_data['latency']):
        if t not in qemu_threads_dict:
            qemu_threads_dict[t] = []
        qemu_threads_dict[t].append(l)
    
    stratovirt_threads_dict = {}
    for t, l in zip(stratovirt_cpu_data['threads'], stratovirt_cpu_data['latency']):
        if t not in stratovirt_threads_dict:
            stratovirt_threads_dict[t] = []
        stratovirt_threads_dict[t].append(l)
    
    threads = sorted(set(qemu_cpu_data['threads']))
    qemu_latency = [calculate_mean(qemu_threads_dict[t]) for t in threads]
    stratovirt_latency = [calculate_mean(stratovirt_threads_dict[t]) for t in threads]
    
    ax.plot(threads, qemu_latency, marker='o', linewidth=2, markersize=8, 
           label='QEMU', color='#3498db')
    ax.plot(threads, stratovirt_latency, marker='s', linewidth=2, markersize=8, 
           label='StratoVirt', color='#e74c3c')
    
    ax.set_xlabel('线程数', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_ylabel('平均延迟 (ms)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_title('CPU性能对比：线程数 vs 延迟', fontsize=14, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.legend(prop=CHINESE_FONT)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'cpu_performance_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ CPU性能对比图已保存: {output_path}")
    plt.close()

def plot_cpu_events_per_sec():
    """3b. CPU性能对比：Threads vs Events/sec"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 按线程数分组并计算平均events per second
    qemu_threads_events_dict = {}
    for t, e in zip(qemu_cpu_data['threads'], qemu_cpu_data['events_per_sec']):
        if t not in qemu_threads_events_dict:
            qemu_threads_events_dict[t] = []
        qemu_threads_events_dict[t].append(e)
    
    stratovirt_threads_events_dict = {}
    for t, e in zip(stratovirt_cpu_data['threads'], stratovirt_cpu_data['events_per_sec']):
        if t not in stratovirt_threads_events_dict:
            stratovirt_threads_events_dict[t] = []
        stratovirt_threads_events_dict[t].append(e)
    
    threads = sorted(set(qemu_cpu_data['threads']))
    qemu_events = [calculate_mean(qemu_threads_events_dict[t]) for t in threads]
    stratovirt_events = [calculate_mean(stratovirt_threads_events_dict[t]) for t in threads]
    
    ax.plot(threads, qemu_events, marker='o', linewidth=2, markersize=8, 
           label='QEMU', color='#3498db')
    ax.plot(threads, stratovirt_events, marker='s', linewidth=2, markersize=8, 
           label='StratoVirt', color='#e74c3c')
    
    ax.set_xlabel('线程数', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_ylabel('Events/sec', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_title('CPU性能对比：线程数 vs Events/sec', fontsize=14, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.legend(prop=CHINESE_FONT)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)
    
    # 添加数值标签
    for i, (q_val, s_val) in enumerate(zip(qemu_events, stratovirt_events)):
        ax.text(threads[i], q_val, f'{q_val:.0f}', ha='center', va='bottom', 
               fontsize=8, color='#3498db')
        ax.text(threads[i], s_val, f'{s_val:.0f}', ha='center', va='top', 
               fontsize=8, color='#e74c3c')
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'cpu_events_per_sec_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ CPU Events/sec对比图已保存: {output_path}")
    plt.close()

def plot_memory_performance():
    """4. 内存性能对比：Block Size vs Events/sec"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    block_sizes = ['1k', '2k', '4k', '8k']
    block_size_numeric = [1, 2, 4, 8]
    
    # Seq模式
    qemu_seq = [calculate_mean(qemu_mem_perf_data[bs]['Seq']) for bs in block_sizes]
    stratovirt_seq = [calculate_mean(stratovirt_mem_perf_data[bs]['Seq']) for bs in block_sizes]
    
    ax1.plot(block_size_numeric, qemu_seq, marker='o', linewidth=2, markersize=8, 
            label='QEMU', color='#3498db')
    ax1.plot(block_size_numeric, stratovirt_seq, marker='s', linewidth=2, markersize=8, 
            label='StratoVirt', color='#e74c3c')
    ax1.set_xlabel('块大小', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax1.set_ylabel('Events/sec', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax1.set_title('顺序访问 (Seq)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(block_size_numeric)
    ax1.set_xticklabels(block_sizes)
    
    # Rnd模式
    qemu_rnd = [calculate_mean(qemu_mem_perf_data[bs]['Rnd']) for bs in block_sizes]
    stratovirt_rnd = [calculate_mean(stratovirt_mem_perf_data[bs]['Rnd']) for bs in block_sizes]
    
    ax2.plot(block_size_numeric, qemu_rnd, marker='o', linewidth=2, markersize=8, 
            label='QEMU', color='#3498db')
    ax2.plot(block_size_numeric, stratovirt_rnd, marker='s', linewidth=2, markersize=8, 
            label='StratoVirt', color='#e74c3c')
    ax2.set_xlabel('块大小', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax2.set_ylabel('Events/sec', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax2.set_title('随机访问 (Rnd)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(block_size_numeric)
    ax2.set_xticklabels(block_sizes)
    
    plt.tight_layout()
    fig.suptitle('内存性能对比：块大小 vs Events/sec', fontsize=14, fontweight='bold', 
                 y=1.0, fontproperties=CHINESE_FONT)
    plt.tight_layout(rect=[0, 0, 1, 0.98])  # 为suptitle留出空间
    output_path = os.path.join(OUTPUT_DIR, 'memory_performance_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 内存性能对比图已保存: {output_path}")
    plt.close()

def plot_io_performance():
    """5. I/O性能对比：不同config的读写吞吐量"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    configs = ['Config1', 'Config2', 'Config3']
    modes = ['seqwr', 'seqrd', 'rndwr', 'rndrd']
    mode_labels = ['顺序写', '顺序读', '随机写', '随机读']
    
    # 准备数据
    qemu_data = []
    stratovirt_data = []
    
    for config_key, config_name in zip(['config1', 'config2', 'config3'], configs):
        for mode, mode_label in zip(modes, mode_labels):
            # QEMU数据
            if 'read' in qemu_io_data[config_key][mode]:
                qemu_val = calculate_mean(qemu_io_data[config_key][mode]['read'])
            else:
                qemu_val = calculate_mean(qemu_io_data[config_key][mode]['written'])
            qemu_data.append(qemu_val)
            
            # StratoVirt数据
            if 'read' in stratovirt_io_data[config_key][mode]:
                stratovirt_val = calculate_mean(stratovirt_io_data[config_key][mode]['read'])
            else:
                stratovirt_val = calculate_mean(stratovirt_io_data[config_key][mode]['written'])
            stratovirt_data.append(stratovirt_val)
    
    x = np.arange(len(configs) * len(modes))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, qemu_data, width, label='QEMU', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, stratovirt_data, width, label='StratoVirt', color='#e74c3c', alpha=0.8)
    
    # 设置x轴标签
    labels = []
    for config in configs:
        for mode_label in mode_labels:
            labels.append(f'{config}\n{mode_label}')
    
    ax.set_xlabel('配置和模式', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_ylabel('吞吐量 (MiB/s)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_title('I/O性能对比：不同配置的读写吞吐量', fontsize=14, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9, fontproperties=CHINESE_FONT)
    ax.legend(prop=CHINESE_FONT)
    ax.grid(axis='y', alpha=0.3)
    
    # 添加数值标签（仅显示较大值）
    for i, (q_val, s_val) in enumerate(zip(qemu_data, stratovirt_data)):
        max_val = max(q_val, s_val)
        if max_val > 100:  # 只显示大于100的值
            ax.text(i, max_val, f'{max_val:.0f}', ha='center', va='bottom', 
                   fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'io_performance_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ I/O性能对比图已保存: {output_path}")
    plt.close()

# ==================== 主函数 ====================

def main():
    """主函数：生成所有图表"""
    print("开始生成实验数据可视化图表...")
    print("=" * 50)
    
    plot_boot_time()
    plot_memory_usage()
    plot_cpu_performance()
    plot_cpu_events_per_sec()
    plot_memory_performance()
    plot_io_performance()
    
    print("=" * 50)
    print("所有图表生成完成！")

if __name__ == '__main__':
    main()

