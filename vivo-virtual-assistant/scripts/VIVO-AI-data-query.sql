 WITH LearningFormsCTE AS (
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
  LEFT JOIN TargetGroupsCTE tgcte ON Id = tgcte.CourseId
