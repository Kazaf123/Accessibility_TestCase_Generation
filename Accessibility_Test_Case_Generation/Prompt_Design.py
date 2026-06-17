import openai
import json
import os
import random


client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_50_few_shot_examples():

    examples = []

    # 1. 组件标签缺失 (Missing semantic label) - 16个
    for i in range(1, 17):
        examples.append({
            "id": f"ML_{i}",
            "issue_type": "Missing semantic label",
            "interaction_path": f"1. Swipe to component_{i}\n2. Verify TalkBack output",
            "java_code": f"""UiObject2 target = device.findObject(By.res("com.example:id/target_{i}"));
CharSequence desc = target.getContentDescription();
if (desc == null || desc.toString().isEmpty()) {{ fail("Missing label"); }}"""
        })

    # 2. 触控目标尺寸不足 (Touch target too small) - 12个
    for i in range(1, 13):
        examples.append({
            "id": f"TS_{i}",
            "issue_type": "Touch target too small",
            "interaction_path": f"1. Locate icon_{i}\n2. Measure bounds",
            "java_code": f"""UiObject2 icon = device.findObject(By.res("com.example:id/icon_{i}"));
Rect bounds = icon.getVisibleBounds();
if (bounds.width() < 48 || bounds.height() < 48) {{ fail("Touch target too small"); }}"""
        })

    # 3. 焦点顺序异常 (Abnormal focus order) - 11个
    for i in range(1, 12):
        examples.append({
            "id": f"FO_{i}",
            "issue_type": "Abnormal focus order",
            "interaction_path": f"1. Swipe right\n2. Check focus traversal",
            "java_code": f"""UiObject2 first = device.findObject(By.res("com.example:id/first_{i}"));
UiObject2 second = device.findObject(By.res("com.example:id/second_{i}"));
if (first.getVisibleBounds().bottom > second.getVisibleBounds().top) {{ fail("Focus order error"); }}"""
        })

    # 4. 动态控件可达性问题 (Dynamic control accessibility) - 11个
    for i in range(1, 12):
        examples.append({
            "id": f"DC_{i}",
            "issue_type": "Dynamic control accessibility",
            "interaction_path": f"1. Scroll down\n2. Interact with dynamic_item_{i}",
            "java_code": f"""UiScrollable scrollable = new UiScrollable(new UiSelector().scrollable(true));
scrollable.scrollIntoView(new UiSelector().resourceId("com.example:id/dynamic_{i}"));
UiObject2 item = device.findObject(By.res("com.example:id/dynamic_{i}"));
if (item == null || !item.isFocusable()) {{ fail("Dynamic control inaccessible"); }}"""
        })
    return examples


FEW_SHOT_DATASET = generate_50_few_shot_examples()


# ==========================================
# 1. 小样本动态检索模块 (In-Context Learning)
# ==========================================
def retrieve_relevant_examples(target_issue_type, all_examples, k=3):

    print(f"[*] 正在从 50 个样本库中检索与 '{target_issue_type}' 相关的小样本...")

    relevant_samples = [ex for ex in all_examples if ex["issue_type"] in target_issue_type]

    if len(relevant_samples) >= k:
        selected_samples = random.sample(relevant_samples, k)
    else:
        other_samples = [ex for ex in all_examples if ex["issue_type"] not in target_issue_type]
        needed = k - len(relevant_samples)
        selected_samples = relevant_samples + random.sample(other_samples, min(needed, len(other_samples)))

    return selected_samples


# ==========================================
# 2. 核心大模型交互方法
# ==========================================
def identify_root_cause(xml_structure, talkback_output):
    """步骤1：问题根控件识别"""
    prompt_1 = f"""
    You are an accessibility tester AI.
    Structure Layer: {xml_structure}
    Semantic Layer: {talkback_output}
    Task: Identify accessibility issues.
    Output JSON: {{"Resource_ID": "...", "Type": "...", "Accessibility_Issue_and_reason": "..."}}
    """
    response = client.chat.completions.create(
        model="gpt-4o", temperature=0.2, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt_1}]
    )
    return json.loads(response.choices[0].message.content)


def infer_interaction_paths(user_goal, component_info, screen_tree_info):
    """步骤2：交互路径推理"""
    prompt_2 = f"""
    User Goal: [{user_goal}]
    Issue: [{component_info['Accessibility_Issue_and_reason']}]
    Target: [{component_info['Resource_ID']}]
    Screen Tree: {screen_tree_info}
    Task: Generate the best interaction path.
    Output JSON: {{"Recommended_Path": "..."}}
    """
    response = client.chat.completions.create(
        model="gpt-4o", temperature=0.2, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt_2}]
    )
    return json.loads(response.choices[0].message.content)["Recommended_Path"]


def generate_uiautomator_script(recommended_path, component_info, retrieved_examples):
    """
    步骤3：无障碍测试用例代码生成 (融合小样本学习)
    """
    print("[步骤3] 执行 Prompt 3: 结合小样本学习生成代码...")

    few_shot_context = ""
    for idx, ex in enumerate(retrieved_examples):
        few_shot_context += f"Example {idx + 1} (Issue: {ex['issue_type']}):\n"
        few_shot_context += f"Path: {ex['interaction_path']}\n"
        few_shot_context += f"Code:\n{ex['java_code']}\n\n"

    prompt_3 = f"""
    -You are an Android UIAutomator test generator.
    -Convert the interaction path into executable Java code.

    Interaction Path to Convert: 
    {recommended_path}

    Target Metadata:
    - resource_id: {component_info['Resource_ID']}
    - issue_type: {component_info['Accessibility_Issue_and_reason']}

    === FEW-SHOT REFERENCE EXAMPLES ===
    Learn from the following {len(retrieved_examples)} examples how to write UIAutomator code for accessibility testing:
    {few_shot_context}
    ===================================

    -Produce Java code using UIAutomator APIs.
    -Do not include explanation outside the code block.
    """

    response = client.chat.completions.create(
        model="gpt-4o", temperature=0.2,
        messages=[{"role": "user", "content": prompt_3}]
    )
    return response.choices[0].message.content


def diagnose_and_fix_script(exec_log, current_script):
    """步骤4：自动修复 (简化示意)"""
    prompt_4 = f"""
    Diagnose and fix the failed script.
    Log: {exec_log}
    Script: {current_script}
    Output JSON: {{"fixed_java_code": "..."}}
    """
    response = client.chat.completions.create(
        model="gpt-4o", temperature=0.2, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt_4}]
    )
    return json.loads(response.choices[0].message.content)['fixed_java_code']


# ==========================================
# 3. 闭环执行管线主干
# ==========================================
def run_accessibility_pipeline():
    print("=== 启动移动应用 GUI 无障碍问题自动测试复现管线 ===")

    xml_struct = "<node resource-id='com.example:id/btn_hot' class='android.widget.Button'/>"
    talkback_output = "Button, unlabelled."
    user_goal = "Tap the hot button"

    component_info = identify_root_cause(xml_struct, talkback_output)
    print(f"[*] 定位控件: {component_info['Resource_ID']} | 问题: {component_info['Accessibility_Issue_and_reason']}")

    recommended_path = infer_interaction_paths(user_goal, component_info, xml_struct)
    print(f"[*] 推荐路径已生成: {recommended_path}")

    retrieved_examples = retrieve_relevant_examples(
        target_issue_type=component_info['Accessibility_Issue_and_reason'],
        all_examples=FEW_SHOT_DATASET,
        k=3
    )

    java_script = generate_uiautomator_script(recommended_path, component_info, retrieved_examples)
    print("[*] 融合小样本学习的 Java 测试脚本生成完毕。")

    print("\n[!] 准备执行部署及后续闭环修复流程 (Step 4)...")
    return java_script


if __name__ == "__main__":
    run_accessibility_pipeline()