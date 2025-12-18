#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验五：不同Token数量下的性能对比
绘制不同token数量（n_token）下两种测试模式（pp, tg200）的 t/s 对比折线图
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
            rcParams['font.sans-serif'] = [font_name, 'PingFang SC', 'STHeiti', 
                                          'Arial Unicode MS', 'Hiragino Sans GB', 'DejaVu Sans']
        else:
            rcParams['font.family'] = 'sans-serif'
            rcParams['font.sans-serif'] = ['PingFang SC', 'STHeiti', 'Arial Unicode MS', 'DejaVu Sans']
            print("⚠ 使用默认中文字体设置")
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

# 从用户提供的数据中提取
# 00-256-4: pp256 = 8.76, tg200 = 8.67
# 200-128-4: pp128 = 7.64, tg200 = 7.62
# 200-64-4: pp64 = 7.89, tg200 = 7.97

n_tokens = [64, 128, 256]  # token数量
pp_tokens_per_sec = [7.89, 7.64, 8.76]  # pp模式（pp64, pp128, pp256）的 t/s
tg200_tokens_per_sec = [7.97, 7.62, 8.67]  # tg200 测试模式的 t/s

# ==================== 图表绘制函数 ====================

def plot_n_token_comparison():
    """绘制不同token数量下两种测试模式的 t/s 对比折线图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制两条折线
    ax.plot(n_tokens, pp_tokens_per_sec, marker='o', linewidth=2, markersize=10, 
           label='pp模式', color='#3498db', alpha=0.8)
    ax.plot(n_tokens, tg200_tokens_per_sec, marker='s', linewidth=2, markersize=10, 
           label='tg200', color='#e74c3c', alpha=0.8)
    
    # 设置标签和标题
    ax.set_xlabel('Token数量 (n_token)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_ylabel('Tokens/sec (t/s)', fontsize=12, fontweight='bold', fontproperties=CHINESE_FONT)
    ax.set_title('不同Token数量下两种测试模式的性能对比', fontsize=14, fontweight='bold', fontproperties=CHINESE_FONT)
    
    # 设置x轴刻度
    ax.set_xticks(n_tokens)
    ax.set_xticklabels(n_tokens)
    
    # 添加图例
    ax.legend(prop=CHINESE_FONT, loc='best')
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加数值标签
    for i, (n, pp_val, tg_val) in enumerate(zip(n_tokens, pp_tokens_per_sec, tg200_tokens_per_sec)):
        ax.text(n, pp_val, f'{pp_val:.2f}', ha='center', va='bottom', 
               fontsize=9, color='#3498db', fontweight='bold')
        ax.text(n, tg_val, f'{tg_val:.2f}', ha='center', va='top', 
               fontsize=9, color='#e74c3c', fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, 'cloud_n_token_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Token数量对比图已保存: {output_path}")
    plt.close()

# ==================== 主函数 ====================

def main():
    """主函数：生成图表"""
    print("开始生成实验五数据可视化图表...")
    print("=" * 50)
    
    plot_n_token_comparison()
    
    print("=" * 50)
    print("所有图表生成完成！")

if __name__ == '__main__':
    main()


