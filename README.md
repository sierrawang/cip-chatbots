# Code in Place Chatbots

This repository contains the code and materials for the paper:
**"The Effects of Chatbot Placement, Personification, and Functionality on Student Outcomes in a Global CS1 Course."**

* **Paper:** [ACM DL Link](https://dl.acm.org/doi/pdf/10.1145/3698205.3729557)
* **Preregistration:** [OSF Link](https://doi.org/10.17605/OSF.IO/QXAZ6)

This study was conducted in **[Code in Place](https://codeinplace.stanford.edu/)**, a free, large-scale, global introductory computer science course. The study explored how chatbot design—such as placement, personification, and functionality—affect student outcomes.

We are sharing this code to promote open science and encourage further research building on this work. This repository contains all of the **publicly shareable code and materials** from the experiment. Some components require integration with your own frontend, backend, or dataset to run.

If you have any questions, contact **Sierra Wang** at **[sierraw@stanford.edu](mailto:sierraw@stanford.edu)**.

## Repository Structure

```
.
├── chatbots/
│   ├── firebase_backend/
│   └── react_frontend/
├── data_analysis/
│   ├── helpers/
│   ├── analyze_course_engagement/
│   ├── analyze_demographics/
│   ├── analyze_messages/
│   └── regression_analysis/
├── download_scripts/
├── downloaded_data/
├── experiment_roster/
├── parsed_data/
└── utils/
```

### Folder Descriptions

* **chatbots/**
  Chatbot implementations used in the experiment. This code was extracted from the Code in Place repositories and is **not standalone**.

  * **firebase\_backend/** – Backend code for chatbot message handling and storage (Firebase).
  * **react\_frontend/** – Frontend chatbot implementations (React).

* **data\_analysis/**
  All scripts used to analyze the experiment data.

  * **helpers/** – Helper functions for statistical analysis, OpenAI API access, and other tools.
  * **analyze\_course\_engagement/** – Scripts for analysis related to course engagement (e.g., comparing assignment completion between experiment groups).
  * **analyze\_demographics/** – Scripts for analysis related to student demographics (e.g., comparing impact of chatbots across genders).
  * **analyze\_messages/** – Scripts for analysis related to chatbot messages (e.g., comparing the types of messages sent by different experiment groups).
  * **regression\_analysis/** – Regression analysis scripts (e.g., regression analysis described in Section 4.4).

* **download\_scripts/**
  Scripts to download and format experiment data from the Code in Place Firestore database.

* **downloaded\_data/**
  Raw experiment data (**not included** in this public repository).

* **experiment\_roster/**
  Roster of participants in the experiment (**not included** in this public repository).

* **parsed\_data/**
  Data that has been cleaned and parsed for further analysis (**not included** in this public repository).

* **utils/**
  Private credentials and miscellaneous utilities (**not included** in this public repository).

---

## Reproducing the Analyses

The following commands will reproduce the tables and figures from the paper.
**Run all commands from the repository root directory.**

### Tables

* **Table 1, Table 2, and Table 3:**

```bash
python3 -m data_analysis.analyze_course_engagement.engagement_tables
```

This command will also produce additional analyses using the complete rosters to verify that excluding students who changed sections does not impact the results.

* **Table 4:**

```bash
python3 -m data_analysis.regression_analysis.regressions_analysis
```

---

### Figures

* **Figure 2:**

```bash
python3 -m data_analysis.analyze_message_classifications.classification_distribution_figure
```

* **Figure 3:**

```bash
python3 -m data_analysis.analyze_message_classifications.analyze_classifications_figure
```

* **Figure 4:**

```bash
python3 -m data_analysis.analyze_demographics.graph_demos
```