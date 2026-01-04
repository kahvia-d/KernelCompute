import os
import uuid
import traceback
from flask import Flask, request, jsonify, send_file

# 从我们其他的模块中导入我们需要的英雄函数
from mcnp_generator import generate_mcnp_input
from task_runner import run_mcnp_task
from data_visualizer import parse_meshtal, plot_flux_distributions

# 创建我们的 Flask 应用
app = Flask(__name__)

# --- API 端点：执行计算 ---
@app.route('/calculate', methods=['POST'])
def calculate_flux():
    """
    API 的核心，接收计算请求，并 orchestrate 整个工作流程。
    """
    # 1. 打开 Coze 寄来的 "包裹"
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    # 2. 从包裹中取出我们需要的三样东西
    core_radius = data.get('core_radius')
    core_height = data.get('core_height')
    fuel_type = data.get('fuel_type')

    if not all([core_radius, core_height, fuel_type]):
        return jsonify({"error": "Missing parameters. Required: core_radius, core_height, fuel_type"}), 400

    # 3. 为这次运行创建一个独一无二的 "房间" (目录)
    run_id = str(uuid.uuid4())
    # 我们将在 'runs' 这个大目录下创建子目录
    run_dir = os.path.join("runs", run_id)
    os.makedirs(run_dir, exist_ok=True)

    try:
        # --- 工作流开始 ---

        # 步骤 A: 生成 MCNP 输入文件
        input_file_path = os.path.join(run_dir, "mcnp_input.inp")
        generate_mcnp_input(core_radius, core_height, fuel_type, input_file_path)

        # 步骤 B: 模拟 MCNP 任务
        # 我们暂时进入那个房间，以确保所有临时文件都生成在里面
        original_dir = os.getcwd()
        os.chdir(run_dir)
        
        success, result = run_mcnp_task("mcnp_input.inp", core_radius, core_height)
        
        # 完成后，回到主目录
        os.chdir(original_dir)
        
        if not success:
            return jsonify({"error": "MCNP simulation (mock) failed", "details": result}), 500

        # meshtal 文件现在有一个绝对路径
        meshtal_path = result

        # 步骤 C: 解析数据并绘制我们心爱的云图
        flux_data = parse_meshtal(meshtal_path)
        # 将 "房间" 地址告诉画师，让他把画保存在正确的地方
        plot_flux_distributions(flux_data, core_radius, core_height, run_dir)
        
        # --- 工作流结束 ---

        # 4. 准备成功的喜报
        # 你的 Render 服务的公开网址，这是构建可访问图片链接的关键
        base_url = "https://kernelcompute.onrender.com" 

        return jsonify({
            "status": "success",
            "run_id": run_id,
            "message": "Calculation (mocked) complete. Plots generated.",
            "plots": {
                "radial": f"{base_url}/results/{run_id}/radial_flux.png",
                "axial": f"{base_url}/results/{run_id}/axial_flux.png"
            }
        })

    except Exception as e:
        # 如果过程中出现任何意外，记录下来并返回错误
        print("An error occurred during the calculation workflow:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- API 端点：提供图片文件 ---
@app.route('/results/<run_id>/<filename>', methods=['GET'])
def get_result_file(run_id, filename):
    """
    这个端点的唯一职责，就是根据 URL 去正确的 "房间" 里找到图片，并展示给用户。
    这是我们最终胜利的关键！
    """
    try:
        # 构建文件的绝对路径，确保无论在哪里都能找到它
        # os.getcwd() -> 获取当前工作目录 (例如 /opt/render/project/src)
        # 然后拼接 'runs', run_id, 和 filename
        file_path = os.path.join(os.getcwd(), 'runs', run_id, filename)

        if not os.path.exists(file_path):
            return jsonify({"error": f"File '{filename}' not found for run_id '{run_id}'"}), 404
        
        # 将文件发送给浏览器
        return send_file(file_path, mimetype='image/png')
    
    except Exception as e:
        print(f"Error serving file: {e}")
        return jsonify({"error": "An internal error occurred while serving the file."}), 500

# --- 本地测试时使用 ---
if __name__ == '__main__':
    # 确保 'runs' 目录存在
    os.makedirs("runs", exist_ok=True)
    # 允许从任何地址访问，方便本地测试
    app.run(host='0.0.0.0', port=5000, debug=True)
