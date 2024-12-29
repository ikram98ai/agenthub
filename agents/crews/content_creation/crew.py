from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool
from pydantic import BaseModel, Field
from typing import List

# groq_llm = "groq/llama-3.1-70b-versatile"
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

class SocialMediaPost(BaseModel):
    platform: str = Field(..., description="The social media platform where the post will be published (e.g., Twitter, LinkedIn).")
    content: str = Field(..., description="The content of the social media post, including any hashtags or mentions.")

class ContentOutput(BaseModel):
    article: str = Field(..., description="The article, formatted in markdown.")
    social_media_posts: List[SocialMediaPost] = Field(..., description="A list of social media posts related to the article.")




@CrewBase
class ContentCreation():
	"""ContentCreation crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@before_kickoff # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs:dict):
		# Example of pulling data from an external API, dynamically changing the inputs
		return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def market_news_monitor_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['market_news_monitor_agent'],
			tools=[SerperDevTool(), ScrapeWebsiteTool()],
			# llm=groq_llm,
		)		

	@agent
	def data_analyst_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['data_analyst_agent'],
    		tools=[SerperDevTool()]#, WebsiteSearchTool()],
		)
	

	@agent
	def content_creator_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['content_creator_agent'],
    		tools=[SerperDevTool()]#, WebsiteSearchTool()],
		)
	
	@agent
	def quality_assurance_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['quality_assurance_agent'],
		)
	

############################################################# TASKS #############################################################


	@task
	def monitor_financial_news_task(self) -> Task:
		return Task(
			config=self.tasks_config['monitor_financial_news'],
			output_file='output/content_creation/monitor_financial_news_task_report.md',
    		agent= self.market_news_monitor_agent()

		)

	@task
	def analyze_market_data_task(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_market_data'],
			output_file='output/content_creation/analyze_market_data_task_report.md',
    		agent=self.data_analyst_agent()

		)
	
	@task
	def create_content_task(self) -> Task:
		return Task(
			config=self.tasks_config['create_content'],
			output_file='output/content_creation/create_content_task_report.md',
			agent=self.content_creator_agent(),
    		context=[self.monitor_financial_news_task(), self.analyze_market_data_task()]

		)
	
	@task
	def quality_assurance_task(self) -> Task:
		return Task(
			config=self.tasks_config['quality_assurance'],
			output_file='output/content_creation/quality_assurance_task_report.md',
			agent=self.quality_assurance_agent(),
    		# output_pydantic=ContentOutput
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ContentCreation crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			verbose=True,
		)
