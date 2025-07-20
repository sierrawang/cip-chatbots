# Code in Place Chatbots

This repository contains the code and materials for the paper:
**"The Effects of Chatbot Placement, Personification, and Functionality on Student Outcomes in a Global CS1 Course."**

* **Paper:** [ACM DL Link](https://dl.acm.org/doi/pdf/10.1145/3698205.3729557)
* **Preregistration:** [OSF Link](https://doi.org/10.17605/OSF.IO/QXAZ6)

This project was part of a study conducted in **[Code in Place](https://codeinplace.stanford.edu/)**, a free, massive, global, introductory computer science course. The study explored how chatbot design choices impact student outcomes.

If you have any questions, feel free to contact **Sierra Wang** at **[sierraw@stanford.edu](mailto:sierraw@stanford.edu)**.

## Repository Structure

```
.
├── chatbots/
├── downloaded_data/
├── download_scripts/
├── data_analysis/
│   ├── helpers/
│   ├── analyze_course_engagement/
│   ├── analyze_demographics/
│   ├── analyze_messages/
│   └── mixed_methods_analysis/
└── utils/
```

### Folder Descriptions

* **chatbots/**
  Chatbot implementations used in the Code in Place website (React-based). These are included here for reference and are not standalone.

* **downloaded\_data/**
  Student data from the experiment (this folder is not included in this public repository due to privacy constraints).
  To understand the data structure, refer to the scripts in `download_scripts/`.

* **download\_scripts/**
  Scripts for downloading the Code in Place student data from Firestore, including code for formatting the data for analysis. These are here for reference, but will not work without official access to the database.

* **data\_analysis/**
  All data analysis code, including:

  * **analyze\_course\_engagement/** – Scripts for analyzing of course engagement.
  * **analyze\_demographics/** – Scripts for analysis related to student demographics.
  * **analyze\_messages/** – Scripts for analyzing chatbot message content.
  * **mixed\_methods\_analysis/** – Scripts for regressions analysis.
  * **helpers/** – Helper functions, for example statistical metrics, OpenAI API connection, and other utilities.

* **utils/**
  Miscellaneous credentials, etc. (private)
