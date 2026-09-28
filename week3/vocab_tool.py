import csv
import os

# 兼容老师的 weekpath 模块，如果报错自动降级使用标准路径
try:
    import weekpath
    DATA_PATH = weekpath.data_path("生词表.csv")
    OUTPUT_PATH = weekpath.root_path("练习.txt")
except Exception:
    print("⚠️ 未加载到 weekpath 模块，将使用默认相对路径定位。")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "data", "生词表.csv")
    OUTPUT_PATH = os.path.join(BASE_DIR, "练习.txt")

# ① 读：读取CSV文件 (使用 csv.DictReader 转换成字典列表)
def load_words(path=DATA_PATH):
    """读取生词表，返回字典列表，并检查表头"""
    if not os.path.exists(path):
        print(f"❌ 错误：找不到数据文件 {path}，请确认 data/生词表.csv 是否存在！")
        return []
    
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        words = list(reader)
        
        # 容错检查（PPT第9页强调 KeyError 的第一大来源）
        if not words:
            print("⚠️ CSV 文件为空！")
            return []
        first_row = words[0]
        if "词汇" not in first_row or "HSK等级" not in first_row or "词性" not in first_row:
            print("❌ 错误：CSV 表头与代码不匹配！请检查你的 CSV 第一行是否包含 '词汇', 'HSK等级', '词性'")
            print(f"当前检测到的表头为：{list(first_row.keys())}")
            return []
            
        return words

# ② 筛：按HSK等级筛选
def filter_by_level(words, level="4"):
    """筛选指定等级的词汇"""
    return [w for w in words if str(w["HSK等级"]).strip() == str(level)]

# ③ 统：统计词性分布 (作业1延伸：使用字典get()方法)
def count_by_pos(words):
    """统计词性"""
    pos_dict = {}
    for w in words:
        pos = w.get("词性", "未知")
        pos_dict[pos] = pos_dict.get(pos, 0) + 1
    return pos_dict

# ④ 写：生成练习题 (作业2扩展：生成造句和填空题)
def gen_exercises(words, out=OUTPUT_PATH):
    """生成练习文件"""
    with open(out, "w", encoding="utf-8") as f:
        # 写入表头提示
        f.write("===== 词语造句练习 =====\n")
        for w in words:
            f.write(f"用“{w['词汇']}”造一个句子。（{w['词性']}）\n")
        
        f.write("\n===== 词语填空练习 =====\n")
        for w in words:
            # 这里用占位符把词语挖空，满足作业2的填空题要求
            f.write(f"请在横线处填入正确的词语：____，意思为：{w['释义']}。（{w['词性']}）\n")
    
    print(f"✅ 已成功生成练习题文件：{out}")

# ================= 主程序运行 =================
if __name__ == "__main__":
    print("====== 华文小助手：生词表处理 ======")
    all_words = load_words()
    
    if all_words:
        print(f"📊 总词汇共 {len(all_words)} 个")
        
        # 筛选 HSK4 词汇
        hsk4_words = filter_by_level(all_words, level="4")
        print(f"📌 其中 HSK4 词汇共 {len(hsk4_words)} 个")
        
        # 统计词性
        pos_stats = count_by_pos(hsk4_words)
        print(f"📈 词性分布: {pos_stats}")
        
        # 生成练习题
        gen_exercises(hsk4_words)
        print("🎉 全部任务完成，去根目录查看 练习.txt 吧！")