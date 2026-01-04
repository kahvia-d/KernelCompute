from flask import Flask, request, jsonify, send_file
import os
import uuid
from mcnp_generator import generate_mcnp_input
# 注意这里的 task_runner 是我们的模拟版本
from task_runner import run_mcnp_task 
from data_visualizer import parse_meshtal, plot_flux_distributions

app = Flask(__name__)
os.makedirs("runs", exist_ok=True)

@app.route('/calculate', methods=['POST'])
def calculate_flux():
    """
    API endpoint to run the full calculation workflow.
    Expects a JSON payload with core_radius, core_height, and fuel_type.
    """
    # !! 就是下面这行代码被遗忘了 !!
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # 现在，我们已经打开了包裹，可以安全地拿出里面的东西了
    core_radius = data.get('core_radius')
    core_height = data.get('core_height')
    fuel_type = data.get('fuel_type')

    if not all([core_radius, core_height, fuel_type]):
        return jsonify({"error": "Missing parameters. Required: core_radius, core_height, fuel_type"}), 400

    # 创建一个唯一的运行目录
    run_id = str(uuid.uuid4())
    run_dir = os.path.join("runs", run_id)
    os.makedirs(run_dir)

    try:
        # --- 步骤 1: 生成 MCNP 输入文件 ---
        input_file_path = os.path.join(run_dir, "mcnp_input.inp")
        generate_mcnp_input(core_radius, core_height, fuel_type, input_file_path)

        # --- 步骤 2: **模拟** MCNP 任务 ---
        original_dir = os.getcwd()
        os.chdir(run_dir)
        
        success, result = run_mcnp_task("mcnp_input.inp", core_radius, core_height)
        
        os.chdir(original_dir)
        
        if not success:
            return jsonify({"error": "MCNP simulation (mock) failed", "details": result}), 500

        meshtal_path = result

        # --- 步骤 3: 解析和可视化 ---
        flux_data = parse_meshtal(meshtal_path)
        
        # !! 修改在这里: 把 run_dir (画室地址) 传递给绘图函数 !!
        # 注意：这里的 radial_plot 和 axial_plot 现在是文件的绝对路径，但我们不需要用它们
        plot_flux_distributions(flux_data, core_radius, core_height, run_dir)
        
        # 你的 Render 服务的公开 URL
        base_url = "https://kernelcompute.onrender.com"

        return jsonify({
            "status": "success",
            "run_id": run_id,
            "message": "Calculation (mocked) complete. Plots generated.",
            "plots": {
                # 我们手动构建正确的 URL
                "radial": f"{base_url}/results/{run_id}/radial_flux.png",
                "axial": f"{base_url}/results/{run_id}/axial_flux.png"
            }
        })

    except Exception as e:
        # 在返回错误时也打印到日志，方便调试
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ... (get_result_file 函数和 app.run 不变) ...