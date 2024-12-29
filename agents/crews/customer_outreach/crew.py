from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

@CrewBase
class CustomerOutreach():

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def sales_rep_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['sales_rep_agent'],
			verbose=True,
			allow_delegation=False,
		)

	@agent
	def lead_sales_rep_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_sales_rep_agent'],
			verbose=True,
			allow_delegation=False,
		)
	
	

############################################################# TASKS #############################################################

	@task
	def lead_profiling_task(self) -> Task:
		return Task(
			config=self.tasks_config['lead_profiling_task'],
			output_file='output/customer_outreach/lead_profiling_task_report.md',
			tools=[search_tool],

		)

	@task
	def personalized_outreach_task(self) -> Task:
		return Task(
			config=self.tasks_config['personalized_outreach_task'],
			output_file='output/customer_outreach/personalized_outreach_task_report.md',
    		tools=[search_tool],

		)
	
	

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			verbose=True,
			# memory=True
		)
