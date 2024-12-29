from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Initialize the tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

from pydantic import BaseModel
# Define a Pydantic model for venue details 
# (demonstrating Output as Pydantic)
class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str

@CrewBase
class EventPlanning():
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def venue_coordinator(self) -> Agent:
		return Agent(
			config=self.agents_config['venue_coordinator'],
			verbose=True,
			tools=[search_tool, scrape_tool],

		)

	@agent
	def logistics_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['logistics_manager'],
			verbose=True,
			tools=[search_tool, scrape_tool],

		)
	
	@agent
	def marketing_communications_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['marketing_communications_agent'],
			verbose=True,
			tools=[search_tool, scrape_tool],

		)
	
	

############################################################# TASKS #############################################################

	@task
	def venue_task(self) -> Task:
		return Task(
			config=self.tasks_config['venue_task'],
			output_file='output/event_planning/venue_task_report.md',
    		output_json=VenueDetails,

		)

	@task
	def logistics_task(self) -> Task:
		return Task(
			config=self.tasks_config['logistics_task'],
			output_file='output/event_planning/logistics_task_report.md',
    		async_execution=True,

		)

	
	@task
	def marketing_task(self) -> Task:
		return Task(
			config=self.tasks_config['marketing_task'],
			output_file='output/event_planning/marketing_task_report.md',
			async_execution=True,

		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
