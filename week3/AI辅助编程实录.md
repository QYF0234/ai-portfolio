# AI辅助编程实录

## 1. 任务与提示词
**要做什么**：读生词表CSV → 筛HSK4 → 统计词性 → 适配练习题。
**我写的提示词（Prompt）**：
> 角色：你是Python教学助手。
> 任务：写脚本处理中文生词表CSV，按HSK等级筛选，统计词性分布，并生成练习题txt。
> 约束条件：只能使用标准库(csv, os)。必须使用 weekpath.root_path() 定位根目录。
> 示例输出：用“坚持”造一个句子。（动词）。

## 2. AI 初版代码
import csv
import weekpath

# 定位数据文件
DATA = weekpath.data_path("生词表.csv")
OUT = weekpath.root_path("练习.txt")

# ① 读：读取CSV
def load_words(path=DATA):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ② 筛：按HSK等级筛选 (AI最初使用传统的for循环)
def filter_by_level(words, level="4"):
    result = []
    for w in words:
        if str(w["HSK等级"]).strip() == str(level):
            result.append(w)
    return result

# ③ 统：统计词性分布 (AI使用了普通的字典键值操作)
def count_by_pos(words):
    d = {}
    for w in words:
        pos = w["词性"]
        if pos in d:
            d[pos] = d[pos] + 1
        else:
            d[pos] = 1
    return d

# ④ 写：生成练习题 (AI最初只生成了造句练习)
def gen_exercises(words, out=OUT):
    with open(out, "w", encoding="utf-8") as f:
        for w in words:
            f.write(f"用“{w['词汇']}”造一个句子。（{w['词性']}）\n")

# 主程序运行
if __name__ == "__main__":
    all_words = load_words()
    hsk4_words = filter_by_level(all_words, level="4")
    pos_stats = count_by_pos(hsk4_words)
    print(f"总词汇: {len(all_words)}, HSK4词汇: {len(hsk4_words)}")
    print(f"词性分布: {pos_stats}")
    gen_exercises(hsk4_words)
    print("练习.txt 生成完毕！")


## 3. 我的修改点（≥3条，重点部分）
1. **修正了字段名防报错**：AI原版直接使用 `w["HSK等级"]`，我根据 PPT 第9页强调的“KeyError 第一大来源”，在代码里加上了表头检查 `if "HSK等级" not in first_row:`，防止不同版本的CSV列名不一致导致崩溃。
2. **增加了路径容错机制**：AI初始代码直接写死了 `weekpath`，如果模块没加载到程序就跑不起来。我修改为 `try...except` 降级方案，保证即使没有 weekpath 也能通过 `os.path` 找到 data 目录。
3. **扩充了作业2要求的扩展功能**：AI初版只生成造句练习题，我修改了 `gen_exercises` 函数，在文件末尾增加了写入“填空题”的逻辑（将目标词替换为 `____`），满足了课后作业要求。
4. **优化了终端输出格式**：AI初版是直接 print 所有词性，我将其修改为字典 `pos_dict.get()` 的形式，更直观地展示了“词性分布”统计（对应老师要求的统一步骤）。

## 4. 最终版 vs 初版差异说明
- **AI哪里想多了**：AI生成了多余的 `argparse` 参数解析器，对于本周作业过于复杂，我将其删除，保持代码简洁。
- **AI哪里漏了**：AI没有对文件不存在 (`FileNotFoundError`) 做处理，我加上了 `if not os.path.exists(path)` 的提前判断。
- **我为什么这么改**：因为老师要求“必须先读懂再改，不要为了炫技写用不到的复杂逻辑”。
