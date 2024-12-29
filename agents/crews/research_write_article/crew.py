from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff


@CrewBase
class ArticleResearchWriter():
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def writer(self) -> Agent:
		return Agent(
			config=self.agents_config['writer'],
			verbose=True,
			allow_delegation=False,
		)

	@agent
	def planner(self) -> Agent:
		return Agent(
			config=self.agents_config['planner'],
			verbose=True,
			allow_delegation=False,
		)
	
	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			verbose=True,
			allow_delegation=False,
		)
	
	

############################################################# TASKS #############################################################

	@task
	def plan_task(self) -> Task:
		return Task(
			config=self.tasks_config['plan'],
			output_file='output/article_research_writer/plan_task_report.md'

		)

	@task
	def write_task(self) -> Task:
		return Task(
			config=self.tasks_config['write'],
			output_file='output/article_research_writer/write_task_report.md'

		)

	
	@task
	def edit_task(self) -> Task:
		return Task(
			config=self.tasks_config['edit'],
			output_file='output/article_research_writer/edit_task_report.md'
		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
