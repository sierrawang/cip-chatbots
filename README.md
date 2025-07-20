# Code in Place Chatbots

This repository contains the code and materials for the paper:
**"The Effects of Chatbot Placement, Personification, and Functionality on Student Outcomes in a Global CS1 Course."**

* **Paper:** [ACM DL Link](https://dl.acm.org/doi/pdf/10.1145/3698205.3729557)
* **Preregistration:** [OSF Link](https://doi.org/10.17605/OSF.IO/QXAZ6)

This project was part of a study conducted in **[Code in Place](https://codeinplace.stanford.edu/)**, a free, large-scale, global introductory computer science course. The study explored how chatbot design choices—such as placement, personification, and functionality—affect student outcomes.

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
  Chatbot implementations used in the experiment. This code was extracted from the Code in Place repositories and is **not standalone**—it is provided for reference and to support future research.

  * **firebase\_backend/** – Backend code for chatbot message handling and storage (Firebase).
  * **react\_frontend/** – Frontend chatbot implementations (React).

* **data\_analysis/**
  All scripts used to analyze the experimental data.

  * **helpers/** – Utility functions for statistical analysis, OpenAI API access, and other tools.
  * **analyze\_course\_engagement/** – Scripts analyzing student course engagement data.
  * **analyze\_demographics/** – Scripts analyzing student demographics.
  * **analyze\_messages/** – Scripts analyzing chatbot message interactions.
  * **regression\_analysis/** – Regression analysis scripts.

* **download\_scripts/**
  Scripts to download and format experimental data from the Code in Place Firestore database.

* **downloaded\_data/**
  Raw experimental data (**not included** in this public repository due to privacy constraints).

* **experiment\_roster/**
  Roster of participants in the experiment (**not included** in this public repository).

* **parsed\_data/**
  Data that has been cleaned and parsed for analysis (**not included** in this public repository).

* **utils/**
  Private credentials and miscellaneous utilities (**not included** in this public repository).
