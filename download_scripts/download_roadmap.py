import sys
sys.path.insert(1, '../utils')
import util

def get_lesson_slides(db, lesson_id):
    lesson_path = f"lessons/cip4/lessonsList/{lesson_id}"
    lesson_data = db.document(lesson_path).get().to_dict()
    return lesson_data["slides"]

def download_roadmap():
    db = util.setup_db()

    rm_path = "roadmap/cip4/modules"
    rm_collection = db.collection(rm_path).stream()
    mod_list = []
    for module in rm_collection:
        module_data = module.to_dict()
        mod_list.append(module_data)

    # order by "startDate" in this format "2024-04-01T22:05"
    all_lessons_in_order = []
    all_assignments_in_order = []
    mod_list.sort(key=lambda x: x["startDate"])
    for module in mod_list:
        if module["roadmapType"] != "student":
            continue
        items_list = module["items"]
        for item in items_list:
            item_type = item["itemType"]
            
            if item_type == "Lesson":
                slides = get_lesson_slides(db, item["completionId"])
                all_lessons_in_order.append((item["completionId"], slides))

            if item_type == "Assignment":
                all_assignments_in_order.append(item["completionId"])

    print(all_lessons_in_order)
    print()
    print(all_assignments_in_order)

if __name__ == "__main__":
    download_roadmap()
