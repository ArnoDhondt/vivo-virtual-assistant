from typing import List
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
import os
import json
import pyodbc
import requests
from collections import defaultdict

class VivoLoader(BaseLoader):
    # Document loader for all content types in the Coman API.
    def __init__(self) -> None:
        self.server = str(os.getenv("VIVO_SERVER"))
        self.database = str(os.getenv("VIVO_DATABASE"))
        self.username = str(os.getenv("VIVO_USERNAME"))
        self.password = str(os.getenv("VIVO_PASSWORD"))

    def loadCoursesThatHaveOffer(self) -> defaultdict:
        url = "https://vivobo-external-production.azurewebsites.net/api/PlannedCourse/FindPlannedCourses"
        headers = {'Authorization': str(os.getenv("ORIS_COMAN_API_KEY")), 'Content-Type': 'application/json'}

        filterBody = {
            "page": {
            "index": 1,
            "size":99999
            }
        }

        response = requests.post(url, json=filterBody, headers=headers)
        # we try to retrieve all the courses and add their planned plannedcourses
        json_response = response.json()
        plannedCourses_list = json_response.get('items')
        course_list = defaultdict(list)
        # iterate list
        for plannedCourse in plannedCourses_list:
            course_id = plannedCourse["course"]["id"]
            plannedCourse_info = plannedCourse["id"]
            #append plannedcourse info to courseId
            course_list[course_id].append(plannedCourse_info)

        return course_list

    def load_data(self, data) -> List[Document]:
        items = []
        
        course_with_offer = self.loadCoursesThatHaveOffer()

        for row in data:
            content = ""
            for item in row:
                content += str(item) + " "

            courseId = str(row[0])

            linkedPlannedCourses = []
            if courseId in course_with_offer:
                linkedPlannedCourses = course_with_offer[courseId]

            document = Document(
                page_content=content,
                source = row[0],
                metadata={
                    "course_id": courseId,
                    "course_title": str(row[1]),
                    "course_knowledge_level": str(row[5]),
                    "course_prior_knowledge_level": str(row[6]),
                    "course_language": str(row[4]),
                    "course_learning_form": str(row[7]),
                    "course_target_groups": str(row[8]),
                    "active_planned_courses": linkedPlannedCourses
                }
            )
            
            items.append(document)

        return items


    def lazy_load(self) -> List[Document]:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )

        try:
            conn = pyodbc.connect(conn_str)

            cursor = conn.cursor()
            cursor.execute("""WITH LearningFormsCTE AS (
                    select clf.CourseId, STRING_AGG(lf.Name, ', ') as LearningForms
                    from CourseLearningForm clf
                    join LearningForm lf on lf.Id = clf.LearningFormId
                    group by clf.CourseId
                ),
                TargetGroupsCTE AS (
                    select ctg.CourseId, STRING_AGG(tg.Title, ', ') as TargetGroups
                    from CourseTargetGroups ctg
                    join TargetGroups tg on tg.Id = ctg.TargetGroupId
                    group by ctg.CourseId
                )

                select [Id], [Title], [CommercialName], [Description], 
                    CASE [Language] WHEN 0 THEN 'Unknown' WHEN 1 THEN 'Dutch' WHEN 2 THEN 'French' WHEN 3 THEN 'German' WHEN 4 THEN 'English' END AS [Language], 
                    CASE [KnowledgeLevel] WHEN 0 THEN 'Unknown' WHEN 1 THEN 'Employee' WHEN 2 THEN 'Worker' END AS [KnowledgeLevel],
                    CASE [PriorKnowledge] WHEN 0 THEN 'Unknown' WHEN 1 THEN 'PreviousModulesAttended' WHEN 2 THEN 'BeginningProfessional' WHEN 3 THEN 'Bachelor' WHEN 4 THEN 'Master' WHEN 5 THEN 'Expert' END AS [PriorKnowledge],
                    lfcte.LearningForms,
                    tgcte.TargetGroups
                from Courses
                LEFT JOIN LearningFormsCTE lfcte ON Id = lfcte.CourseId
                LEFT JOIN TargetGroupsCTE tgcte ON Id = tgcte.CourseId""")
            data = cursor.fetchall() # DateTime cannot be fetched

            conn.close()

            return self.load_data(data)

        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")