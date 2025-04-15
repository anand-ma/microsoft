import os
import streamlit as st
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

def setup_agents():
    """Setup and return the travel planning agents"""
    # Get API key from Streamlit secrets
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getnev("MODEL")
    model_client = OpenAIChatCompletionClient(model=model, api_key=api_key)

    planner_agent = AssistantAgent(
        "planner_agent",
        model_client=model_client,
        description="A helpful assistant that can plan trips.",
        system_message="You are a helpful assistant that can suggest a travel plan for a user based on their request.",
    )

    local_agent = AssistantAgent(
        "local_agent",
        model_client=model_client,
        description="A local assistant that can suggest local activities or places to visit.",
        system_message="You are a helpful assistant that can suggest authentic and interesting local activities or places to visit for a user and can utilize any context information provided.",
    )

    itinerary_optimization_agent = AssistantAgent(
        "itinerary_optimization_agent",
        model_client=model_client,
        description="A helpful assistant that can provide an itinerary according to geographic proximity.",
        system_message="You are a helpful assistant that can review travel plans, providing feedback. You are an itinerary optimization agent responsible for rearranging travel itineraries so that destinations are visited in geographic order to optimize time and travel distance. When provided with an itinerary containing various destinations or points of interest, analyze the geographical locations of these spots and reorder the itinerary so that every subsequent location is close to the previous one. Your goal is to minimize the overall distance traveled and avoid backtracking. Use mapping data or coordinate approximations as needed to determine proximity. Additionally, ensure that any constraints given in the initial itinerary (such as opening hours or priority visits) are respected unless they conflict with the primary goal of reducing travel distance. Provide clear explanations for any modifications you suggest, and include both the original and the optimized itinerary. ",
    )

    travel_summary_agent = AssistantAgent(
        "travel_summary_agent",
        model_client=model_client,
        description="A helpful assistant that can summarize the travel plan.",
        system_message="You are a helpful assistant that can take in all of the suggestions and advice from the other agents and provide a detailed final travel plan. You must ensure that the final plan is integrated and complete. YOUR FINAL RESPONSE MUST BE THE COMPLETE PLAN. When the plan is complete and all perspectives are integrated, you can respond with TERMINATE.",
    )

    return [planner_agent, local_agent, itinerary_optimization_agent, travel_summary_agent]

async def get_travel_plan(user_request):
    """Get travel plan from the group chat"""
    agents = setup_agents()
    termination = TextMentionTermination("TERMINATE")
    group_chat = RoundRobinGroupChat(agents, termination_condition=termination)
    
    # Run the chat and yield responses as they come in
    async for response in group_chat.run_stream(task=user_request):
        yield response 
