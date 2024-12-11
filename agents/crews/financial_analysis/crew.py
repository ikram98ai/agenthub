from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

from crewai_tools import ScrapeWebsiteTool, SerperDevTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Uncomment the following line to use an example of a custom tool
# from financial_analysis.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

@CrewBase
class FinancialAnalysis():
	"""FinancialAnalysis crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# @before_kickoff # Optional hook to be executed before the crew starts
	# def pull_data_example(self, inputs:dict):
	# 	# Example of pulling data from an external API, dynamically changing the inputs
	# 	# inputs['extra_data'] = "This is extra data"
	# 	return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def data_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['data_analyst'],
			verbose=True,
			allow_delegation=True,
			tools = [scrape_tool, search_tool]
		)

	@agent
	def trading_strategy(self) -> Agent:
		return Agent(
			config=self.agents_config['trading_strategy'],
			verbose=True,
			allow_delegation=True,
			tools = [scrape_tool, search_tool]
		)
	
	@agent
	def execution_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['execution_agent'],
			verbose=True,
			allow_delegation=True,
			tools = [scrape_tool, search_tool]
		)
	
	@agent
	def risk_management(self) -> Agent:
		return Agent(
			config=self.agents_config['risk_management'],
			verbose=True,
			allow_delegation=True,
			tools = [scrape_tool, search_tool]
		)

############################################################# TASKS #############################################################

	@task
	def data_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['data_analysis_task'],
			output_file='output/financial_analysis/data_analysis_task_report.md'

		)

	@task
	def strategy_development_task(self) -> Task:
		return Task(
			config=self.tasks_config['strategy_development_task'],
			output_file='output/financial_analysis/strategy_development_task_report.md'

		)
	
	@task
	def execution_planning_task(self) -> Task:
		return Task(
			config=self.tasks_config['execution_planning_task'],
			output_file='output/financial_analysis/execution_planning_task_report.md'

		)
	
	
	@task
	def risk_assessment_task(self) -> Task:
		return Task(
			config=self.tasks_config['risk_assessment_task'],
			output_file='output/financial_analysis/risk_assessment_task_report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the FinancialAnalysis crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
