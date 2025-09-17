# -*- coding: utf-8 -*-
# @Time    : 2025/07/15
# @Author  : 小黄呀呀呀
# @公众号 : 小黄鸭科研笔记
# @File    : gui_surface_plotter.py
# @Software: Python 3.x
# @Description: 一个带GUI的工具，用于加载2D图像，通过鼠标选择一个区域，并将其转换为3D曲面图进行可视化。

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Surface3DApp:
    """
    主应用程序类，包含所有的GUI组件和功能逻辑。
    """
    def __init__(self, master):
        """
        应用程序的构造函数，初始化窗口和所有变量。
        """
        self.master = master
        self.master.title("2D图像转3D曲面图工具")
        
        # 初始化核心变量
        self.image_path = None       # 存储当前加载图片的路径
        self.pil_image = None        # Pillow库的Image对象
        self.tk_image = None         # Tkinter兼容的PhotoImage对象
        self.selection_rect = None   # 画布上用于显示选框的矩形ID
        self.crop_box = None         # 存储选定区域的坐标元组 (left, top, right, bottom)
        self.start_x = None          # 鼠标拖拽选区的起始X坐标
        self.start_y = None          # 鼠标拖拽选区的起始Y坐标

        # --- 创建GUI组件 ---

        # 顶部框架，用于放置按钮
        top_frame = tk.Frame(master, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        # 加载图片按钮
        self.load_button = tk.Button(top_frame, text="1. 加载图片", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # 生成3D图按钮，初始为禁用状态
        self.plot_button = tk.Button(top_frame, text="2. 生成3D图", command=self.generate_plot, state=tk.DISABLED)
        self.plot_button.pack(side=tk.LEFT, padx=5)

        # 底部框架，用于放置图片和提示信息
        bottom_frame = tk.Frame(master, padx=10, pady=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # 提示标签，向用户提供操作指引
        self.info_label = tk.Label(bottom_frame, text="请先加载一张图片，然后在图片上拖拽鼠标以选择区域。")
        self.info_label.pack(pady=5)
        
        # 用于显示图片的画布，设置鼠标指针为十字形
        self.canvas = tk.Canvas(bottom_frame, cursor="cross", bg="lightgrey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- 绑定鼠标事件到画布 ---
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)    # 鼠标左键按下
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)         # 鼠标左键拖动
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release) # 鼠标左键释放

    def load_image(self):
        """
        打开文件对话框让用户选择图片，并将其显示在画布上。
        """
        path = filedialog.askopenfilename(
            title="请选择一张图片文件",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"), ("All files", "*.*")]
        )
        if not path:
            return

        self.image_path = path
        try:
            # 使用Pillow加载图片
            self.pil_image = Image.open(self.image_path)
            # 转换为Tkinter可用的格式
            self.tk_image = ImageTk.PhotoImage(self.pil_image)
            
            # 调整画布大小以精确匹配图片尺寸
            self.canvas.config(width=self.pil_image.width, height=self.pil_image.height)
            # 在画布上显示图片
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            
            # 更新状态
            self.info_label.config(text=f"图片已加载。请在图片上拖拽鼠标选择区域。")
            self.plot_button.config(state=tk.DISABLED)
            self.crop_box = None
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None

        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片: {e}")
            self.image_path = None

    def on_mouse_press(self, event):
        """鼠标按下事件处理：记录起始点，并创建选框。"""
        if not self.pil_image: return
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        # 创建一个红色的矩形选框
        self.selection_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        """鼠标拖拽事件处理：实时更新选框大小。"""
        if not self.start_x or not self.start_y: return
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        # 更新矩形坐标
        self.canvas.coords(self.selection_rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_release(self, event):
        """鼠标释放事件处理：最终确定选区并保存坐标。"""
        if not self.start_x or not self.start_y: return
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        # 计算并确保坐标是 (左, 上, 右, 下) 的顺序
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)
        
        # 检查选区大小是否有效，避免过小的选区
        if right - left > 5 and bottom - top > 5:
            self.crop_box = (int(left), int(top), int(right), int(bottom))
            self.plot_button.config(state=tk.NORMAL) # 激活“生成3D图”按钮
            self.info_label.config(text=f"已选择区域: {self.crop_box}。可以点击按钮生成3D图。")
        else:
            self.info_label.config(text="选择的区域太小，请重新选择。")
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
            self.crop_box = None
            self.plot_button.config(state=tk.DISABLED)

        # 重置起始点
        self.start_x, self.start_y = None, None

    def generate_plot(self):
        """
        核心功能：根据选择的区域生成并显示3D曲面图。
        """
        if not self.image_path or not self.crop_box:
            messagebox.showwarning("警告", "请先加载图片并有效选择一个区域。")
            return
        
        try:
            # 1. 裁剪图片
            cropped_img = self.pil_image.crop(self.crop_box)
            
            # 2. 转换为灰度图，其像素值将作为Z轴数据
            gray_img = cropped_img.convert('L')
            z_data = np.array(gray_img)

            # 3. 创建X和Y的网格坐标
            height, width = z_data.shape
            X, Y = np.meshgrid(np.arange(width), np.arange(height))

            # 4. 创建3D图形和坐标轴
            fig = plt.figure(figsize=(10, 7))
            ax = fig.add_subplot(111, projection='3d')

            # 5. 绘制3D曲面图
            ax.plot_surface(X, Y, z_data, cmap='jet', rstride=1, cstride=1, antialiased=True)

            # 6. 美化图形外观，使其更像示例
            ax.view_init(elev=60, azim=-45) # 设置视角
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0)) # 隐藏背景面板
            ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.grid(False) # 隐藏网格线
            plt.title("3D Surface Plot of Selected Region")
            
            # 7. 显示Matplotlib绘图窗口
            plt.show()

        except Exception as e:
            messagebox.showerror("绘图错误", f"生成3D图时发生错误: {e}")

if __name__ == '__main__':
    # 创建主窗口
    root = tk.Tk()
    # 实例化应用
    app = Surface3DApp(root)
    # 进入主事件循环
    root.mainloop()

