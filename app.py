#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataCleanPro - 数据清洗专家
简单兼容的桌面数据清洗工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
import chardet
import json
from datetime import datetime
import threading
import os
import sys

class DataCleanPro:
    """数据清洗专家主应用程序 - 简化版"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("DataCleanPro - 数据清洗专家")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # 居中显示
        self.center_window()
        
        # 键盘快捷键
        self.root.bind('<Control-o>', lambda e: self.select_file())
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_variables(self):
        """初始化变量"""
        self.df_original = None
        self.df_current = None
        self.file_path = None
        self.cleaning_history = []
        
        # 进度相关
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="就绪 - 请选择数据文件")
        
        # 清洗选项
        self.missing_action = tk.StringVar(value="无操作")
        self.duplicate_action = tk.StringVar(value="无操作")
        self.outlier_action = tk.StringVar(value="无操作")
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部标题
        title_frame = tk.Frame(main_frame, bg='#E3F2FD', relief='ridge', bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="🧹 DataCleanPro - 数据清洗专家", 
                              font=('微软雅黑', 16, 'bold'), 
                              bg='#E3F2FD', fg='#1976D2')
        title_label.pack(pady=10)
        
        # 创建左右分栏
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        self.create_control_panel(content_frame)
        
        # 右侧数据展示区域
        self.create_data_panel(content_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
        
    def create_control_panel(self, parent):
        """创建左侧控制面板"""
        # 控制面板框架
        control_frame = tk.LabelFrame(parent, text="控制面板", font=('微软雅黑', 10, 'bold'))
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 文件操作区域
        file_frame = tk.LabelFrame(control_frame, text="📁 文件操作", 
                                  font=('微软雅黑', 9, 'bold'))
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 快捷选择区域
        quick_frame = tk.Frame(file_frame, bg='#F5F5F5', relief='solid', bd=1)
        quick_frame.pack(fill=tk.X, padx=5, pady=5)
        
        quick_label = tk.Label(quick_frame, text="🎯 点击快速选择文件\n支持: CSV | Excel | JSON",
                              font=('微软雅黑', 9), bg='#F5F5F5', fg='#666666')
        quick_label.pack(pady=10)
        
        # 绑定点击事件
        quick_frame.bind('<Button-1>', lambda e: self.select_file())
        quick_label.bind('<Button-1>', lambda e: self.select_file())
        
        # 文件操作按钮
        tk.Button(file_frame, text="📂 选择数据文件", command=self.select_file,
                 bg='#2196F3', fg='white', font=('微软雅黑', 9)).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(file_frame, text="⚡ 加载数据", command=self.load_data,
                 bg='#4CAF50', fg='white', font=('微软雅黑', 9)).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(file_frame, text="💾 保存结果", command=self.save_data,
                 bg='#FF9800', fg='white', font=('微软雅黑', 9)).pack(fill=tk.X, padx=5, pady=2)
        
        # 数据清洗区域
        clean_frame = tk.LabelFrame(control_frame, text="🧹 数据清洗", 
                                   font=('微软雅黑', 9, 'bold'))
        clean_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 清洗选项
        tk.Label(clean_frame, text="缺失值处理:", font=('微软雅黑', 8)).pack(anchor=tk.W, padx=5, pady=2)
        missing_combo = ttk.Combobox(clean_frame, textvariable=self.missing_action, 
                                    values=["无操作", "删除含缺失值的行", "删除含缺失值的列", 
                                          "均值填充", "中位数填充", "众数填充"], 
                                    state="readonly", font=('微软雅黑', 8))
        missing_combo.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(clean_frame, text="重复值处理:", font=('微软雅黑', 8)).pack(anchor=tk.W, padx=5, pady=2)
        duplicate_combo = ttk.Combobox(clean_frame, textvariable=self.duplicate_action,
                                      values=["无操作", "删除重复行", "标记重复行"],
                                      state="readonly", font=('微软雅黑', 8))
        duplicate_combo.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(clean_frame, text="异常值处理:", font=('微软雅黑', 8)).pack(anchor=tk.W, padx=5, pady=2)
        outlier_combo = ttk.Combobox(clean_frame, textvariable=self.outlier_action,
                                    values=["无操作", "IQR方法", "Z-score方法"],
                                    state="readonly", font=('微软雅黑', 8))
        outlier_combo.pack(fill=tk.X, padx=5, pady=2)
        
        # 执行按钮
        tk.Button(clean_frame, text="🚀 执行清洗", command=self.execute_cleaning,
                 bg='#F44336', fg='white', font=('微软雅黑', 9, 'bold')).pack(fill=tk.X, padx=5, pady=10)
        
        # 数据分析区域
        analysis_frame = tk.LabelFrame(control_frame, text="📊 数据分析", 
                                      font=('微软雅黑', 9, 'bold'))
        analysis_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(analysis_frame, text="📈 数据概览", command=self.show_data_overview,
                 font=('微软雅黑', 8)).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(analysis_frame, text="📋 质量报告", command=self.show_quality_report,
                 bg='#673AB7', fg='white', font=('微软雅黑', 8)).pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(analysis_frame, text="📜 清洗历史", command=self.show_cleaning_history,
                 font=('微软雅黑', 8)).pack(fill=tk.X, padx=5, pady=2)
        
    def create_data_panel(self, parent):
        """创建右侧数据展示面板"""
        # 数据面板框架
        data_frame = tk.LabelFrame(parent, text="📊 数据展示", font=('微软雅黑', 10, 'bold'))
        data_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建Notebook用于标签页
        self.notebook = ttk.Notebook(data_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据预览标签页
        self.create_data_preview_tab()
        
        # 统计信息标签页
        self.create_stats_tab()
        
    def create_data_preview_tab(self):
        """创建数据预览标签页"""
        preview_frame = tk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="📋 数据预览")
        
        # 创建表格显示区域
        table_frame = tk.Frame(preview_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview显示数据
        columns = ["列1", "列2", "列3", "列4", "列5"]
        self.data_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_stats_tab(self):
        """创建统计信息标签页"""
        stats_frame = tk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 统计信息")
        
        # 使用ScrolledText显示统计信息
        self.stats_text = scrolledtext.ScrolledText(stats_frame, font=('Consolas', 9), wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        status_frame = tk.Frame(parent, relief='sunken', bd=1)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 进度条
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # 状态标签
        status_label = tk.Label(status_frame, textvariable=self.status_var, font=('微软雅黑', 8))
        status_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def select_file(self):
        """选择数据文件"""
        filetypes = [
            ("所有支持的格式", "*.csv;*.xlsx;*.xls;*.json"),
            ("CSV文件", "*.csv"),
            ("Excel文件", "*.xlsx;*.xls"), 
            ("JSON文件", "*.json"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=filetypes
        )
        
        if filename:
            file_ext = Path(filename).suffix.lower()
            if file_ext in ['.csv', '.xlsx', '.xls', '.json']:
                self.file_path = filename
                self.status_var.set(f"✅ 已选择: {Path(filename).name}")
                
                if messagebox.askyesno("确认", f"是否立即加载文件?\n{Path(filename).name}"):
                    self.load_data()
            else:
                messagebox.showwarning("格式错误", 
                                     f"不支持的文件格式: {file_ext}\n\n"
                                     "请选择以下格式:\n"
                                     "• CSV文件 (.csv)\n"
                                     "• Excel文件 (.xlsx, .xls)\n"
                                     "• JSON文件 (.json)")
                self.status_var.set("❌ 文件格式不支持")
                
    def load_data(self):
        """加载数据文件"""
        if not self.file_path:
            messagebox.showwarning("警告", "请先选择数据文件!")
            return
            
        threading.Thread(target=self._load_data_thread, daemon=True).start()
        
    def _load_data_thread(self):
        """在后台线程中加载数据"""
        try:
            self.status_var.set("正在加载数据...")
            self.progress_var.set(20)
            
            file_path = Path(self.file_path)
            file_ext = file_path.suffix.lower()
            
            self.progress_var.set(40)
            
            if file_ext == '.csv':
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
                df = pd.read_csv(file_path, encoding=encoding)
                
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                
            elif file_ext == '.json':
                df = pd.read_json(file_path)
                
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            self.progress_var.set(80)
            
            self.df_original = df.copy()
            self.df_current = df.copy()
            self.cleaning_history = []
            
            self.progress_var.set(100)
            
            self.root.after(0, self._update_ui_after_load)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("加载错误", f"加载文件失败:\n{str(e)}"))
            self.root.after(0, lambda: self.status_var.set("❌ 加载失败"))
            self.root.after(0, lambda: self.progress_var.set(0))
            
    def _update_ui_after_load(self):
        """数据加载完成后更新UI"""
        self.update_data_preview()
        self.update_stats_display()
        self.status_var.set(f"✅ 加载成功 - {len(self.df_current)}行 × {len(self.df_current.columns)}列")
        self.progress_var.set(0)
        
    def update_data_preview(self):
        """更新数据预览"""
        if self.df_current is None:
            return
            
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        df = self.df_current
        columns = list(df.columns)
        
        # 限制显示列数
        max_cols = 8
        display_columns = columns[:max_cols] if len(columns) > max_cols else columns
        
        # 配置列
        self.data_tree["columns"] = display_columns
        for col in display_columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100, minwidth=60)
            
        # 添加数据行 (限制100行)
        max_rows = 100
        display_rows = min(len(df), max_rows)
        
        for i in range(display_rows):
            row_data = []
            for col in display_columns:
                value = df.iloc[i][col]
                if pd.isna(value):
                    row_data.append("(空)")
                else:
                    str_value = str(value)
                    if len(str_value) > 20:
                        str_value = str_value[:17] + "..."
                    row_data.append(str_value)
                    
            self.data_tree.insert("", "end", values=row_data)
            
        if len(df) > max_rows:
            self.data_tree.insert("", "end", values=["..."] * len(display_columns))
            
    def update_stats_display(self):
        """更新统计信息显示"""
        if self.df_current is None:
            return
            
        df = self.df_current
        
        stats_text = "=== 数据基本信息 ===\n\n"
        stats_text += f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列\n"
        stats_text += f"内存使用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB\n\n"
        
        stats_text += "=== 数据类型统计 ===\n"
        for dtype, count in df.dtypes.value_counts().items():
            stats_text += f"{dtype}: {count} 列\n"
        stats_text += "\n"
        
        stats_text += "=== 数据质量评估 ===\n"
        missing_stats = df.isnull().sum()
        total_missing = missing_stats.sum()
        stats_text += f"总缺失值: {total_missing}\n"
        
        if total_missing > 0:
            stats_text += "缺失值分布:\n"
            for col, count in missing_stats[missing_stats > 0].items():
                percentage = count / len(df) * 100
                stats_text += f"  {col}: {count} ({percentage:.1f}%)\n"
        stats_text += "\n"
        
        duplicate_count = df.duplicated().sum()
        stats_text += f"重复行数: {duplicate_count}\n"
        if duplicate_count > 0:
            percentage = duplicate_count / len(df) * 100
            stats_text += f"重复率: {percentage:.1f}%\n"
        stats_text += "\n"
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats_text += "=== 数值列统计 ===\n"
            for col in numeric_cols[:3]:  # 只显示前3列
                series = df[col]
                stats_text += f"\n{col}:\n"
                stats_text += f"  计数: {series.count()}\n"
                stats_text += f"  均值: {series.mean():.2f}\n"
                stats_text += f"  标准差: {series.std():.2f}\n"
                stats_text += f"  最小值: {series.min()}\n"
                stats_text += f"  最大值: {series.max()}\n"
                
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        
    def execute_cleaning(self):
        """执行数据清洗"""
        if self.df_current is None:
            messagebox.showwarning("警告", "请先加载数据!")
            return
            
        threading.Thread(target=self._execute_cleaning_thread, daemon=True).start()
        
    def _execute_cleaning_thread(self):
        """在后台线程中执行清洗"""
        try:
            self.status_var.set("正在执行数据清洗...")
            self.progress_var.set(0)
            
            df = self.df_current.copy()
            operations = []
            
            # 缺失值处理
            self.progress_var.set(25)
            if self.missing_action.get() == "删除含缺失值的行":
                before_count = len(df)
                df = df.dropna()
                after_count = len(df)
                operations.append(f"删除含缺失值的行: {before_count - after_count} 行")
                
            elif self.missing_action.get() == "删除含缺失值的列":
                before_cols = len(df.columns)
                df = df.dropna(axis=1)
                after_cols = len(df.columns)
                operations.append(f"删除含缺失值的列: {before_cols - after_cols} 列")
                
            elif self.missing_action.get() in ["均值填充", "中位数填充", "众数填充"]:
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    if self.missing_action.get() == "均值填充":
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        operations.append("使用均值填充数值列缺失值")
                    elif self.missing_action.get() == "中位数填充":
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
                        operations.append("使用中位数填充数值列缺失值")
                    elif self.missing_action.get() == "众数填充":
                        for col in numeric_cols:
                            mode_val = df[col].mode()
                            if not mode_val.empty:
                                df[col] = df[col].fillna(mode_val.iloc[0])
                        operations.append("使用众数填充数值列缺失值")
            
            # 重复值处理
            self.progress_var.set(50)
            if self.duplicate_action.get() == "删除重复行":
                before_count = len(df)
                df = df.drop_duplicates()
                after_count = len(df)
                operations.append(f"删除重复行: {before_count - after_count} 行")
                
            elif self.duplicate_action.get() == "标记重复行":
                df['是否重复'] = df.duplicated()
                duplicate_count = df['是否重复'].sum()
                operations.append(f"标记重复行: {duplicate_count} 行")
            
            # 异常值处理
            self.progress_var.set(75)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if self.outlier_action.get() == "IQR方法" and len(numeric_cols) > 0:
                before_count = len(df)
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                after_count = len(df)
                operations.append(f"IQR方法处理异常值: 移除 {before_count - after_count} 行")
                
            elif self.outlier_action.get() == "Z-score方法" and len(numeric_cols) > 0:
                before_count = len(df)
                for col in numeric_cols:
                    z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                    df = df[z_scores < 3]
                after_count = len(df)
                operations.append(f"Z-score方法处理异常值: 移除 {before_count - after_count} 行")
            
            self.progress_var.set(100)
            
            self.df_current = df
            self.cleaning_history.extend(operations)
            
            self.root.after(0, self._update_ui_after_cleaning, operations)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("清洗错误", f"数据清洗失败:\n{str(e)}"))
            self.root.after(0, lambda: self.status_var.set("❌ 清洗失败"))
            self.root.after(0, lambda: self.progress_var.set(0))
            
    def _update_ui_after_cleaning(self, operations):
        """数据清洗完成后更新UI"""
        self.update_data_preview()
        self.update_stats_display()
        
        operation_text = "\n".join(operations) if operations else "无操作"
        self.status_var.set(f"✅ 清洗完成 - {len(self.df_current)}行 × {len(self.df_current.columns)}列")
        self.progress_var.set(0)
        
        if operations:
            messagebox.showinfo("清洗完成", f"数据清洗完成!\n\n执行的操作:\n{operation_text}")
        
    def save_data(self):
        """保存清洗结果"""
        if self.df_current is None:
            messagebox.showwarning("警告", "没有数据可保存!")
            return
            
        filetypes = [
            ("CSV文件", "*.csv"),
            ("Excel文件", "*.xlsx"),
            ("JSON文件", "*.json")
        ]
        
        filename = filedialog.asksaveasfilename(
            title="保存清洗结果",
            filetypes=filetypes,
            defaultextension=".csv"
        )
        
        if filename:
            try:
                file_path = Path(filename)
                file_ext = file_path.suffix.lower()
                
                if file_ext == '.csv':
                    self.df_current.to_csv(filename, index=False, encoding='utf-8-sig')
                elif file_ext == '.xlsx':
                    self.df_current.to_excel(filename, index=False)
                elif file_ext == '.json':
                    self.df_current.to_json(filename, orient='records', force_ascii=False, indent=2)
                    
                messagebox.showinfo("保存成功", f"数据已保存到:\n{filename}")
                self.status_var.set("✅ 数据保存成功")
                
            except Exception as e:
                messagebox.showerror("保存错误", f"保存文件失败:\n{str(e)}")
                
    def show_data_overview(self):
        """显示数据概览"""
        if self.df_current is None:
            messagebox.showwarning("警告", "请先加载数据!")
            return
        self.notebook.select(1)  # 切换到统计信息标签页
        
    def show_quality_report(self):
        """显示数据质量报告"""
        if self.df_current is None:
            messagebox.showwarning("警告", "请先加载数据!")
            return
            
        report_window = tk.Toplevel(self.root)
        report_window.title("数据质量报告")
        report_window.geometry("500x400")
        
        df = self.df_current
        
        report_text = "=== 数据质量评估报告 ===\n\n"
        
        # 完整性评分
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness = (1 - missing_cells / total_cells) * 100
        report_text += f"数据完整性: {completeness:.1f}%\n"
        
        # 一致性评分
        duplicate_rate = df.duplicated().sum() / len(df) * 100
        consistency = 100 - duplicate_rate
        report_text += f"数据一致性: {consistency:.1f}%\n"
        
        report_text += f"\n总体质量评分: {(completeness + consistency) / 2:.1f}%\n\n"
        
        report_text += "=== 详细分析 ===\n\n"
        
        # 各列质量分析
        report_text += "各列质量分析:\n"
        for col in df.columns:
            missing_rate = df[col].isnull().sum() / len(df) * 100
            quality_score = 100 - missing_rate
            report_text += f"  {col}: {quality_score:.1f}%"
            if missing_rate > 0:
                report_text += f" (缺失{missing_rate:.1f}%)"
            report_text += "\n"
            
        # 建议
        report_text += "\n=== 清洗建议 ===\n"
        
        if missing_cells > 0:
            high_missing_cols = df.columns[df.isnull().sum() / len(df) > 0.5]
            if len(high_missing_cols) > 0:
                report_text += f"• 建议删除缺失值超过50%的列: {list(high_missing_cols)}\n"
                
        if df.duplicated().sum() > 0:
            report_text += f"• 发现 {df.duplicated().sum()} 行重复数据，建议删除\n"
        
        text_widget = scrolledtext.ScrolledText(report_window, font=('Consolas', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, report_text)
        text_widget.config(state=tk.DISABLED)
        
    def show_cleaning_history(self):
        """显示清洗历史"""
        if not self.cleaning_history:
            messagebox.showinfo("历史记录", "暂无清洗历史记录")
            return
            
        history_window = tk.Toplevel(self.root)
        history_window.title("清洗历史记录")
        history_window.geometry("400x300")
        
        history_text = "=== 数据清洗历史记录 ===\n\n"
        history_text += f"原始数据: {self.df_original.shape[0]}行 × {self.df_original.shape[1]}列\n"
        history_text += f"当前数据: {self.df_current.shape[0]}行 × {self.df_current.shape[1]}列\n\n"
        
        history_text += "执行的操作:\n"
        for i, operation in enumerate(self.cleaning_history, 1):
            history_text += f"{i}. {operation}\n"
            
        text_widget = scrolledtext.ScrolledText(history_window, font=('微软雅黑', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, history_text)
        text_widget.config(state=tk.DISABLED)
        
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        print("🚀 启动 DataCleanPro - 数据清洗专家...")
        print("📊 版本: 2.1.2 (简化兼容版)")
        print("🎨 特性: 简洁界面 + 快捷选择")
        print("⚡ 快捷键: Ctrl+O 快速选择文件")
        print("🔧 兼容性: 支持所有tkinter版本")
        print("-" * 50)
        
        app = DataCleanPro()
        app.run()
    except Exception as e:
        print(f"❌ 应用程序启动失败: {e}")
        print("💡 解决建议:")
        print("1. 检查Python版本 (需要3.8+)")
        print("2. 确认依赖包已安装: pip install -r requirements.txt")
        print("3. 检查tkinter是否可用: python -m tkinter")
        input("\n按回车键退出...")

if __name__ == "__main__":
    main() 