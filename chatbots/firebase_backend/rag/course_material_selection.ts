import * as functions from "firebase-functions";
import { LookupMaterial } from "./course_material_types";
import { LESSON_OUTLINE } from "./course_material_lookup_table"

const selectRandomItem = (items: any[]): any => {
    return items[Math.floor(Math.random() * items.length)];
}

// Choose the item using the following logic:
// 1. Prioritize the item for the given lesson
// 2. If no items are available for the given lesson, choose an item for the most recent lesson
// 3. If no prior items exist, choose an item for the soonist upcoming lesson
const selectItemBasedOnLesson = (items: any[], lessonId: string): any => {
    functions.logger.log("selectItemBasedOnLesson", items, lessonId);

    const lessonIndex = LESSON_OUTLINE[lessonId];
    functions.logger.log("lessonIndex", lessonIndex);
    
    if (lessonIndex === -1) {
        functions.logger.log("Invalid lessonId in selectItemBasedOnLesson", lessonId);
        return selectRandomItem(items);
    }

    // Prioritize the item from this lesson
    const lessonItems = items.filter(item => item.lessonId === lessonId);
    if (lessonItems.length > 0) {
        functions.logger.log("selected item from current lesson");
        return selectRandomItem(lessonItems);
    }

    // Choose a item from the most recent lesson
    for (let i = lessonIndex - 1; i >= 1; i--) {
        functions.logger.log("choosing from lesson i -", i);
        const lessonI = Object.keys(LESSON_OUTLINE).filter(key => LESSON_OUTLINE[key] === i)[0];
        const recentLessonItems = items.filter(item => item.lessonId === lessonI);
        if (recentLessonItems.length > 0) {
            return selectRandomItem(recentLessonItems);
        }
    }

    // Choose a reading for the soonist upcoming lesson
    for (let i = lessonIndex + 1; i < LESSON_OUTLINE.length; i++) {
        functions.logger.log("choosing from lesson i +", i);
        const lessonI = Object.keys(LESSON_OUTLINE).filter(key => LESSON_OUTLINE[key] === i)[0];
        const upcomingLessonItems = items.filter(item => item.lessonId === lessonI);
        if (upcomingLessonItems.length > 0) {
            return selectRandomItem(upcomingLessonItems);
        }
    }

    functions.logger.log("selectItemBasedOnLesson logic is flawed");
    return selectRandomItem(items);
}


// Randomly choose an example from the list of examples
const chooseExample = (examples: LookupMaterial[]): LookupMaterial => {
    return selectRandomItem(examples);
}

// Select a lecture video based on the current lesson
const chooseLecture = (lectures: LookupMaterial[], lessonId: string): LookupMaterial => {
    return selectItemBasedOnLesson(lectures, lessonId);
}

// Select a reading based on the current lesson
const chooseReading = (readings: LookupMaterial[], lessonId: string): LookupMaterial => {
    return selectItemBasedOnLesson(readings, lessonId);
}

// Randomly choose an assignment from the list of assignments
const chooseAssignment = (assignments: LookupMaterial[]): LookupMaterial => {
    return selectRandomItem(assignments);
}

// (5)
// Given a list of all possible materials, prioritize the most relevant ones.
// Returns a list of the prioritized materials.
export const prioritizeMaterials = (materials: LookupMaterial[], lessonId: string): LookupMaterial[] => {
    const examples = materials.filter(item => item.type === "code example");
    const lectures = materials.filter(item => item.type === "lecture video");
    const readings = materials.filter(item => item.type === "python textbook chapter" || item.type === "karel textbook chapter");
    const assignments = materials.filter(item => item.type === "assignment");
    const docs = materials.filter(item => item.type === "code documentation");

    const prioritized_materials = [];
    if (examples.length > 0) {
        prioritized_materials.push(chooseExample(examples));
    }

    if (lectures.length > 0) {
        prioritized_materials.push(chooseLecture(lectures, lessonId));
    }

    if (readings.length > 0) {
        prioritized_materials.push(chooseReading(readings, lessonId));
    }

    if (assignments.length > 0) {
        prioritized_materials.push(chooseAssignment(assignments));
    }

    // Add all the documentation
    prioritized_materials.push(...docs);

    return prioritized_materials;
}