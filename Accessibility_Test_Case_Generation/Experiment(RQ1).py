import json
import time
from pipeline import run_accessibility_pipeline  # 假设核心管线保存在 pipeline.py 中


def run_rq1_rq4_evaluation(dataset_path, model_name="gpt-4o", max_retries=5):
    """
    RQ1 & RQ4 评估脚本
    :param dataset_path: 包含待测 App GUI 信息和无障碍问题描述的 JSON 数据集
    :param model_name: 用于 RQ4 对比的不同大模型名称
    """
    print(f"=== 启动 RQ1/RQ4 评估 | 模型: {model_name} | 数据集: {dataset_path} ===")

    # 初始化统计指标
    metrics = {
        "total_issues": 0,
        "execution_success": 0,  # ER 分子
        "reproduction_success": 0,  # RR 分子
        "total_time_seconds": 0
    }

    # 加载评估数据集 (示例结构)
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    for app_data in dataset:
        metrics["total_issues"] += 1
        issue_id = app_data['issue_id']
        print(f"\n[测试用例 {issue_id}] 开始评估...")

        start_time = time.time()

        try:
            # 调用核心管线 (这里需在管线内部支持 model_name 参数的切换)
            # 返回结果应包含：是否执行成功，是否复现问题，以及生成的代码
            exec_success, repro_success, final_script = run_accessibility_pipeline(
                gui_url=app_data['screenshot_url'],
                xml_struct=app_data['xml_hierarchy'],
                talkback_output=app_data['talkback_text'],
                user_goal=app_data['user_goal'],
                few_shot_dataset=FEW_SHOT_DATASET,
                model=model_name,
                max_iterations=max_retries
            )

            if exec_success:
                metrics["execution_success"] += 1
            if repro_success:
                metrics["reproduction_success"] += 1

        except Exception as e:
            print(f"[错误] 测试用例 {issue_id} 评估异常: {str(e)}")

        metrics["total_time_seconds"] += (time.time() - start_time)

    # 计算最终指标
    rr_rate = (metrics["reproduction_success"] / metrics["total_issues"]) * 100
    er_rate = (metrics["execution_success"] / metrics["total_issues"]) * 100
    avg_time = metrics["total_time_seconds"] / metrics["total_issues"]

    print("\n" + "=" * 40)
    print(f"评估完成 | 模型: {model_name}")
    print(f"问题总数: {metrics['total_issues']}")
    print(f"执行成功率 (ER): {er_rate:.1f}%")
    print(f"问题复现率 (RR): {rr_rate:.1f}%")
    print(f"平均生成时间 (AGT): {avg_time:.2f} 秒")
    print("=" * 40)

    return metrics