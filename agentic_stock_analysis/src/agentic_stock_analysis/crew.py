from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List
from datetime import datetime

from agentic_stock_analysis.tools import (
    stock_news_search, market_trending_tickers, sector_performance,
    stock_fundamentals, compare_stocks, stock_historical_data,
    stock_prediction, batch_stock_predictions, anomaly_detection,
)

# LLM Configuration
default_llm = LLM(model="gpt-4o-mini", temperature=0.7)
planner_llm = LLM(model="anthropic/claude-3-haiku-20240307", temperature=0.5)
senior_writer_llm = LLM(model="gpt-4o", temperature=0.3)


@CrewBase
class AgenticStockAnalysis():
    """Autonomous Multi-Agent Stock Research Orchestrator"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[stock_news_search, market_trending_tickers, sector_performance, SerperDevTool()],
            llm=default_llm, verbose=True
        )
    
    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            tools=[stock_fundamentals, compare_stocks, stock_historical_data],
            llm=default_llm, verbose=True
        )
    
    @agent
    def ml_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['ml_engineer'],
            tools=[stock_prediction, batch_stock_predictions, anomaly_detection, stock_historical_data],
            llm=default_llm, verbose=True
        )
    
    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            tools=[], llm=planner_llm, verbose=True
        )
    
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            tools=[], llm=default_llm, verbose=True
        )
    
    @agent
    def senior_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_writer'],
            tools=[], llm=senior_writer_llm, verbose=True
        )

    @task
    def research_daily_market(self) -> Task:
        return Task(config=self.tasks_config['research_daily_market'])
    
    @task
    def analyze_stock_fundamentals(self) -> Task:
        return Task(config=self.tasks_config['analyze_stock_fundamentals'])
    
    @task
    def run_stock_prediction_model(self) -> Task:
        return Task(config=self.tasks_config['run_stock_prediction_model'])
    
    @task
    def create_stock_plan(self) -> Task:
        return Task(config=self.tasks_config['create_stock_plan'])
    
    @task
    def write_stock_report(self) -> Task:
        return Task(config=self.tasks_config['write_stock_report'])
    
    @task
    def review_and_finalize_report(self) -> Task:
        return Task(
            config=self.tasks_config['review_and_finalize_report'],
            output_file=f'reports/daily_stock_report_{datetime.now().strftime("%Y-%m-%d")}.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, tasks=self.tasks,
            process=Process.sequential, verbose=True,
            memory=True, respect_context_window=True,
        )
