def run_rq3_repair_evaluation(failed_scripts_dataset):
    """
    RQ3 自动修复成功率评估脚本
    :param failed_scripts_dataset: 包含初次执行失败的脚本及报错日志的数据集
    """
    print("=== 启动 RQ3 闭环修复自适应评估 ===")

    metrics = {
        "ar_total": len(failed_scripts_dataset),  # AR_total: 初次执行失败的脚本数
        "ar_succ": 0  # AR_succ: 修复后成功复现的脚本数
    }

    for failed_case in failed_scripts_dataset:
        print(f"正在修复用例: {failed_case['id']}...")

        current_script = failed_case['initial_java_script']
        xml_struct = failed_case['xml_hierarchy']
        intended_path = failed_case['intended_path']

        is_fixed = False
        # 按照论文方法，最大迭代修复 5 次
        for attempt in range(5):
            # 模拟执行失败的用例，获取执行日志
            success, exec_log = mock_device_execution(current_script)

            if success:
                is_fixed = True
                break

            # 执行 Prompt 4 进行诊断与重构
            current_script = diagnose_and_fix_script(
                execution_log=exec_log,
                ui_tree=xml_struct,
                intended_trace=intended_path,
                current_script=current_script
            )

        if is_fixed:
            metrics["ar_succ"] += 1
            print(f"用例 {failed_case['id']} 修复成功！(迭代次数: {attempt + 1})")
        else:
            print(f"用例 {failed_case['id']} 修复失败 (达到最大迭代 5 次)。")

    # 计算 ARSR
    if metrics["ar_total"] > 0:
        arsr = (metrics["ar_succ"] / metrics["ar_total"]) * 100
    else:
        arsr = 0.0

    print("\n" + "=" * 40)
    print("RQ3 修复效果评估完成")
    print(f"初次执行失败脚本数 (AR_total): {metrics['ar_total']}")
    print(f"修复成功脚本数 (AR_succ): {metrics['ar_succ']}")
    print(f"自动修复成功率 (ARSR): {arsr:.1f}%")
    print("=" * 40)

    return arsr