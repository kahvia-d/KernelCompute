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
    # ... (前面的代码不变) ...
    core_radius = data.get('core_radius')
    core_height = data.get('core_height')
    fuel_type = data.get('fuel_type')

    # ... (参数检查代码不变) ...

    # 创建运行目录
    run_id = str(uuid.uuid4())
    run_dir = os.path.join("runs", run_id)
    os.makedirs(run_dir)

    try:
        # --- 步骤 1: 生成 MCNP 输入文件 (这一步保留，因为它是流程的一部分) ---
        input_file_path = os.path.join(run_dir, "mcnp_input.inp")
        generate_mcnp_input(core_radius, core_height, fuel_type, input_file_path)

        # --- 步骤 2: **模拟** MCNP 任务 ---
        original_dir = os.getcwd()
        os.chdir(run_dir)
        
        # !! 修改在这里: 把 core_radius 和 core_height 传递给模拟函数 !!
        success, result = run_mcnp_task("mcnp_input.inp", core_radius, core_height)
        
        os.chdir(original_dir)
        
        if not success:
            return jsonify({"error": "MCNP simulation (mock) failed", "details": result}), 500

        meshtal_path = result

        # --- 步骤 3: 解析和可视化 (这一步完全不受影响) ---
        # 注意：因为我们的假数据生成逻辑在 task_runner.py 中，所以 data_visualizer.py
        # 的解析逻辑可能需要微调以匹配我们伪造的格式。
        # 但我上面的伪造函数已经尽量模仿了真实格式，所以大概率无需修改。
        flux_data = parse_meshtal(meshtal_path)
        radial_plot, axial_plot = plot_flux_distributions(flux_data, core_radius, core_height)
        
        return jsonify({
            "status": "success",
            "run_id": run_id,
            "message": "Calculation (mocked) complete. Plots generated.",
            "plots": {
                "radial": f"/results/{run_id}/radial_flux.png",
                "axial": f"/results/{run_id}/axial_flux.png"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ... (get_result_file 函数和 app.run 不变) ...