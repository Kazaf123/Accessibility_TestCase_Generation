def run_rq2_ablation_study(dataset_path, ablation_target):
    """
    RQ2 消融实验脚本
    :param ablation_target: 待移除的模块名称，例如 "-Prompt 1", "-小样本学习"
    """
    print(f"=== 启动 RQ2 消融实验 | 移除模块: {ablation_target} ===")

    # 配置消融标志
    config = {
        "use_prompt_1": True,
        "use_prompt_2": True,
        "use_prompt_3": True,
        "use_prompt_4": True,
        "use_few_shot": True,
        "use_structured_prompt": True
    }

    if ablation_target == "-Prompt 1":
        config["use_prompt_1"] = False
    elif ablation_target == "-Prompt 2":
        config["use_prompt_2"] = False
    elif ablation_target == "-Prompt 3":
        config["use_prompt_3"] = False
    elif ablation_target == "-Prompt 4":
        config["use_prompt_4"] = False
    elif ablation_target == "-小样本学习":
        config["use_few_shot"] = False
    elif ablation_target == "无结构Prompt":
        config["use_structured_prompt"] = False

    metrics = {"total": 0, "rr_success": 0, "er_success": 0}

    # 模拟遍历数据集
    for app_data in load_mock_dataset(dataset_path):
        metrics["total"] += 1

        # 在执行核心管线时传入消融配置
        # 管线内部需要根据这些布尔值跳过对应步骤（例如跳过 Prompt 1 时使用随机或基于规则的控件选择）
        exec_success, repro_success, _ = run_pipeline_with_ablation(
            app_data,
            config=config
        )

        if exec_success: metrics["er_success"] += 1
        if repro_success: metrics["rr_success"] += 1

    rr = (metrics["rr_success"] / metrics["total"]) * 100
    er = (metrics["er_success"] / metrics["total"]) * 100
    print(f"[{ablation_target}] RR: {rr:.1f}% | ER: {er:.1f}%")