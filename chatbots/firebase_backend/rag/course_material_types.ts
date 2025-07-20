// The following types are used to represent the course materials 

// Description returned by GPT of a course material
export type MaterialDescription = {
    type: string;
    concept: string;
}

// Course material info used for the lookup process
// This is the type of all of the elements in MATERIALS_LOOKUP_TABLE
export type LookupMaterial = {
    type: string;
    docId?: string;
    lessonId?: string;
    title: string;
    tags: string;
};

// Course material info used for the generation process
// This is the type of all of the elements in MATERIALS_DESCRIPTIONS
export type CourseMaterial = {
    content: string;
    url: string;
    hasCompleted: boolean;
    title: string;
    type: string;
};
