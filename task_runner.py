import os
import time
import numpy as np

def _generate_fake_meshtal(output_path: str, nx: int, ny: int, nz: int, core_radius: float, core_height: float):
    """
    生成一个伪造的 meshtal 文件，数据由数学函数创建。
    """
    # 创建坐标网格
    x = np.linspace(-core_radius, core_radius, nx)
    y = np.linspace(-core_radius, core_radius, ny)
    z = np.linspace(-core_height / 2, core_height / 2, nz)
    xv, yv, zv = np.meshgrid(x, y, z, indexing='ij')

    # 使用高斯函数 + 余弦函数模拟通量分布
    # 中心高，边缘低；轴向中间高，两端低
    radial_decay = np.exp(-(xv**2 + yv**2) / (2 * (core_radius / 2)**2))
    axial_shape = np.cos(np.pi * zv / core_height)
    
    # 组合成三维通量场并添加一些随机噪声
    flux_data = radial_decay * axial_shape * 1e13 + np.random.rand(nx, ny, nz) * 1e11
    flux_data[flux_data < 0] = 0 # 保证通量非负

    # 伪造 meshtal 文件头
    header = f"""\
    Mesh Tally Number   4
    
    This is a fake meshtal file generated for demonstration.
    
    Mesh defined on tally     4
    X direction:  {x[0]:.5E} to {x[-1]:.5E} by {nx} points
    Y direction:  {y[0]:.5E} to {y[-1]:.5E} by {ny} points
    Z direction:  {z[0]:.5E} to {z[-1]:.5E} by {nz} points
    
    Energy         Tally         Rel Error
    """

    # 写入文件
    with open(output_path, 'w') as f:
        f.write(header)
        # MCNP输出格式是 Z->Y->X 循环
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    # 伪造数据行，随便写几个值
                    line = f" {x[i]:.5E} {y[j]:.5E} {z[k]:.5E} {flux_data[i, j, k]:.5E} 0.01\n"
                    f.write(line)
    print(f"Generated fake meshtal file at '{output_path}'")


def run_mcnp_task(
    input_file: str,
    # 接收额外参数用于生成假数据
    core_radius: float, 
    core_height: float,
) -> (bool, str):
    """
    模拟 MCNP 运行，不进行真实计算，而是直接生成伪造的结果文件。
    """
    print("Simulating MCNP run... This will take a few seconds.")
    time.sleep(3) # 假装在计算

    # 定义网格分辨率，与 mcnp_generator.py 中的 Tally 设置对应
    # 在真实项目中，这些参数也应该传递过来
    NX, NY, NZ = 50, 50, 20

    meshtal_file = "meshtal"
    
    try:
        # 调用新函数生成假数据文件
        _generate_fake_meshtal(meshtal_file, NX, NY, NZ, core_radius, core_height)
        
        print("MCNP simulation completed successfully (mocked).")
        return True, os.path.abspath(meshtal_file)
        
    except Exception as e:
        message = f"Failed to generate fake meshtal file: {e}"
        print(message)
        return False, message
