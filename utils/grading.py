# utils/grading.py

import openai
import re
import pandas as pd
import docx
import io
import os
from datetime import datetime
from dotenv import load_dotenv
from database.connection import get_db_connection
import streamlit as st

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")



# Add this new function to handle text formatting
def format_text_for_display(raw_text):
    """
    Use AI to reformat text for better readability
    Returns formatted text or original text if error occurs
    """
    system_prompt = """You are a document formatting expert. Reformart the provided text with proper:
    - Paragraph separation
    - List formatting
    - Heading hierarchy
    - Consistent indentation
    - Clear section breaks
    Preserve all original content while improving readability. Output should be plain text only."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Formatting error: {str(e)}")
        return raw_text


# Add this new function in your utils/grading.py or in the current file
def convert_rubric_to_table(rubric_text):
    """Convert rubric text to formatted table using OpenAI"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Convert this rubric to a markdown table with columns Criteria, Ratings, and Descriptions."},
                {"role": "user", "content": f"Here is the rubric: {rubric_text}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error processing rubric: {str(e)}")
        return None


# def FetchAssignment_Rubrics(name):
#     if "Individual Assignment- Research & Discovery" in name:
#         # return "**Effect on reader** is 20 points (score full 20 points if it ticks all boxes and has wow-factor. Remove 8 point if it doesn't tick all but ticks majority of the boxes and is also interesting to reader. Remove 16 points if its off topic and going no where, and it ticks a minority of the boxes), **Project problem/idea** is 20 points (score full 20 points if the project idea is clearly stated and solves a real-life problem that is feasible, and is supported by three literature sources. Remove 8 points if it has all of the requirements but does not reflect why the researcher wants to do the project. Remove 16 points if the project idea is unclear and not a real life problem and is not feasible), **methodology** is 20 points (score full 20 points if methodology to be followed is clearly stated and fits well with the problem and perfectly feasible. Remove 8 points if the student submission has all the requirements and fits the project problem but needs some improvements. Remove 16 points if the project plan lacks an explanation of the to be followed methodology, and also if the researcher seems to lack any awareness of this methodology's limitations and possible solution to those), **end product** is 20 marks. **Submission before deadline** is 20 marks (score full 20 points if student wrote in their report if they exceeded deadline or not, and if they did not include it in their report they score 10 marks).   *** Total Points: 0 out of 100"
#         return "correctness 10% and quality of solution 90%"
    
#     elif "Individual Assignment- Assumption Testing" in name:
#         # return "**Effect on reader** is 20 points (score full 20 points if it ticks all boxes and has wow-factor. Remove 8 point if it doesn't tick all but ticks majority of the boxes and is also interesting to reader. Remove 16 points if its off topic and going no where, and it ticks a minority of the boxes), **Project problem/idea** is 20 points (score full 20 points if the project idea is clearly stated and solves a real-life problem that is feasible, and is supported by three literature sources. Remove 8 points if it has all of the requirements but does not reflect why the researcher wants to do the project. Remove 16 points if the project idea is unclear and not a real life problem and is not feasible), **methodology** is 20 points (score full 20 points if methodology to be followed is clearly stated and fits well with the problem and perfectly feasible. Remove 8 points if the student submission has all the requirements and fits the project problem but needs some improvements. Remove 16 points if the project plan lacks an explanation of the to be followed methodology, and also if the researcher seems to lack any awareness of this methodology's limitations and possible solution to those), **end product** is 20 marks. **Submission before deadline** is 20 marks (score full 20 points if student wrote in their report if they exceeded deadline or not, and if they did not include it in their report they score 10 marks).   *** Total Points: 0 out of 100"
#         return "correctness 10% and quality of solution 90%"


    
#     elif "W2- Individual Assignment- Framing a Problem" in name:
#         return """**Time Management** is 10 marks (score full marks 10/10 marks if the work states that the Assignment was Submitted before the deadline. score 8/10 if the works states that the Assignment was Submitted max 2 days after the deadline.. score 6/10 if the works states that the Assignment was Submitted 3-7 days after the deadline. score 4/10 if the works states that that submission was More than 1 week late, that is, Assignment Submitted 8-14 days after the deadline. score 2/10 if the works states that the Assignment was Submitted more than 2 weeks after the deadline.). **Impact of Problem-Framing on Project Direction** is 30 marks (score full marks 30/30 marks if The reflection provides a comprehensive and insightful analysis of how problem-framing significantly influenced the project’s direction, showcasing a deep understanding of the connection between problem definition and subsequent design decisions. The response clearly illustrates how problem-framing led to innovative opportunities within the project. score 24/30 marks if The analysis effectively explains the impact of problem-framing on the project’s direction, demonstrating a solid grasp of the subject. The response identifies some innovative outcomes that resulted from framing the problem but lacks the depth or breadth seen in higher-level responses. score 9/30 marks if The reflection shows limited understanding of how problem-framing influenced the project. The response is vague, with little evidence of how the framing affected the direction of the design thinking process. score 0/30 marks if The reflection lacks clarity and does not adequately address the influence of problem-framing on the project. There is minimal to no connection made between the framing and the project’s outcomes. **Challenges in Defining the Problem and Resolution** is 20 marks (score full marks 20/20 marks if The response offers a thorough and insightful discussion of the challenges faced in defining the problem, highlighting complex issues such as biases and assumptions. and if The strategies used to address these challenges are well-articulated, showing a clear, evidence-based approach. score 16/20 marks if The response discusses the challenges encountered in problem definition, with a clear explanation of the strategies employed to overcome them and if There is a good understanding of biases and assumptions, though the analysis could be more detailed. score 6/20 marks if The response identifies a few challenges in problem definition but provides limited detail on how they were resolved, and if There is little consideration of biases and assumptions, indicating a superficial understanding. score 0/20 marks if The response fails to adequately identify challenges or strategies used to address them, and if There is no meaningful discussion of biases, assumptions, or other complexities in problem definition. **Effectiveness of the Design Brief** is 20 marks (score full marks 20/20 marks if The reflection provides a nuanced evaluation of the design brief's effectiveness in guiding the project, identifying its strengths and limitations with clarity, and if The analysis is well-supported by examples from the project, demonstrating a strong understanding of how a well-crafted design brief shapes project outcomes. score 16/20 marks if The reflection evaluates the design brief effectively, noting key strengths and limitations, also While the analysis is solid, it could benefit from deeper insight or more comprehensive examples to illustrate the points made. score 6/20 marks if The reflection provides a limited evaluation of the design brief, focusing more on the brief’s shortcomings than its strengths, and if The discussion is vague and lacks supporting examples or in-depth analysis. score 0/20 marks if The reflection does not adequately evaluate the design brief's effectiveness, and if The response is unclear or off-topic, with little to no critical analysis of the brief's role in the project. **Strategies for Improved Problem-Framing and Design Brief Creation** is 20 marks (score full marks 20/20 marks if The response proposes advanced, practical strategies for improving problem-framing and design brief creation in future projects, and if The suggestions are clearly rooted in the experiences and insights gained during the current project and show a strong ability to prioritize user needs and project goals. score 16/20 marks if The response provides solid strategies for improving future problem-framing and design briefs, with clear connections to the current project and if The suggestions are practical but might lack the innovative thinking or depth required for an excellent rating. score 6/20 marks if The reflection provides limited strategies for future improvement, with vague or underdeveloped ideas, and if The response lacks a strong connection to the current project, indicating a superficial approach to learning from experience. score 0/20 marks if The reflection fails to offer meaningful strategies for future improvement, and if The suggestions are either irrelevant or so vague that they do not demonstrate a clear understanding of how to enhance problem-framing or design brief creation.

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 
    
#     elif "W3- Project Assignment- Make Your Plans" in name:
#         return """**Time Management** is 10 marks (score full marks 10/10 marks if the work states that the Assignment was Submitted before the deadline. score 8/10 if the works states that the Assignment was Submitted max 2 days after the deadline.. score 6/10 if the works states that the Assignment was Submitted 3-7 days after the deadline. score 4/10 if the works states that that submission was More than 1 week late, that is, Assignment Submitted 8-14 days after the deadline. score 2/10 if the works states that the Assignment was Submitted more than 2 weeks after the deadline.).**Clarity and Feasibility of Planned Activities** is 30 marks (score full marks 30/30 marks if The project plan clearly outlines a detailed sequence of activities that are logically structured and demonstrate a thorough understanding of the project’s scope and if The plan is adaptable, reflecting awareness of potential changes and uncertainties in the project lifecycle. score 24/30 marks if The project plan outlines a well-organized sequence of activities, though minor adjustments may be needed for better clarity or feasibility and if The plan acknowledges uncertainties but could benefit from more detailed contingency considerations. score 12/30 marks if The project plan presents an incomplete or poorly structured sequence of activities, with significant gaps in feasibility and insufficient consideration of potential changes. score 6/30 marks if The project plan is unclear, with an illogical or incoherent sequence of activities, lacking any adaptability to project changes or uncertainties. **Identification and Engagement Strategy for Stakeholders** is 30 marks (score full marks 30/30 marks if The people plan thoroughly identifies all relevant stakeholders, detailing their relationships to the project and specific roles. The engagement strategy is well-developed, clearly outlining how to secure support and communicate effectively with each stakeholder. score 24/30 marks if The people plan identifies most key stakeholders with clear roles and relationships. The engagement strategy is solid but may lack depth in addressing how to manage potential stakeholder challenges. score 12/30 marks if The people plan only identifies some stakeholders, with vague or unclear roles and relationships. The engagement strategy is underdeveloped, leaving significant gaps in how to ensure stakeholder involvement. score 6/30 marks if The people plan fails to identify key stakeholders or their roles, and lacks any coherent engagement strategy, jeopardizing the project's success. **Comprehensiveness and Relevance of Research Strategy** is 30 marks (score full marks 30/30 marks if The research plan is comprehensive, with well-defined research questions, a clear target population, and an appropriate number of interviews, and if It demonstrates a robust strategy for gathering and triangulating data, ensuring all relevant topics are explored thoroughly. score 24/30 marks if The research plan is detailed and covers the key research questions and target population, but could be slightly enhanced by refining the data gathering or triangulation strategy. score 12/30 marks if The research plan is underdeveloped, missing important research questions or failing to adequately define the target population and if The data gathering strategy is weak, and triangulation is not clearly addressed. score 6/30 marks if The research plan is inadequate, lacking clear research questions, an identifiable target population, or any coherent strategy for data gathering and analysis, severely limiting the project's foundation.

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 
    
#     elif "W3- Individual Assignment- Planning" in name:
#         return """**Time Management** is 10 marks (score full marks 10/10 marks if the work states that the Assignment was Submitted before the deadline. score 8/10 if the works states that the Assignment was Submitted max 2 days after the deadline.. score 6/10 if the works states that the Assignment was Submitted 3-7 days after the deadline. score 4/10 if the works states that that submission was More than 1 week late, that is, Assignment Submitted 8-14 days after the deadline. score 2/10 if the works states that the Assignment was Submitted more than 2 weeks after the deadline.).  **Stakeholder Prioritization and Effectiveness** is 30 marks (score full marks 30/30 marks if The prioritization of stakeholders is based on a well-reasoned and strategic analysis, demonstrating a deep understanding of stakeholder roles and project goals. The approach is innovative and highly likely to be effective in practice. score 24/30 marks if The stakeholder prioritization is logical and mostly well-reasoned, with minor areas for improvement in strategic alignment. The approach is sound and likely to be effective. score 12/30 marks if The stakeholder prioritization is weak or unclear, with limited justification and weak alignment with project goals. The approach is unlikely to be fully effective. score 6/30 marks if The prioritization lacks coherence and justification, showing little understanding of stakeholder roles or project goals. The approach is ineffective. **Structuring Engagement and Research Through Stakeholder Questions** is 30 marks (score full marks 30/30 marks if The formulation of stakeholder questions is insightful, strategically structured, and closely aligned with research objectives and project goals and The questions effectively guide the engagement and research process. score 24/30 marks if The questions are well-formulated and structured with minor areas for improvement. The approach is mostly aligned with research objectives and effectively supports engagement. score 12/30 marks if The questions are loosely structured and may not fully support research objectives or engagement goals. The approach is unlikely to be highly effective. score 6/30 marks if The questions lack structure and coherence, failing to support the research objectives or engagement effectively. The approach is ineffective. **Adaptability and Embracing Uncertainty in Project Planning** is 30 marks (score full marks 30/30 marks if The reflection demonstrates a high level of confidence and preparedness for adapting to changes and managing uncertainty. Clear and proactive steps are outlined for harnessing change and embracing the iterative nature of design thinking. score 24/30 marks if The reflection shows solid confidence and readiness to adapt, with a well-considered approach to managing uncertainty. Minor improvements could enhance the effectiveness of the plan. score 12/30 marks if The reflection shows limited confidence in adaptability, with vague or incomplete strategies for managing uncertainty. The approach is reactive rather than proactive. score 6/30 marks if The reflection lacks a coherent plan for adapting to changes or managing uncertainty, showing little understanding of the importance of flexibility in design thinking. The approach is ineffective.

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 

    
#     elif "Project Plan" in name:
#         return """**Effect on reader** is 20 marks (score full 20/20 marks if it ticks all boxes and has wow-factor. score 16/20 marks if it doesn't tick all but ticks majority of the boxes and is also interesting to reader. scores 8/20 marks if its off topic and going no where, and it ticks a minority of the boxes).  **Project problem/idea** is 20 marks (score full 20/20 marks if the project idea is clearly stated and solves a real-life problem that is feasible, and is supported by three literature sources. score 16/20 marks if it has all of the requirements but does not reflect why the researcher wants to do the project. score 8/20 marks if the project idea is unclear and not a real life problem and is not feasible).  **methodology** is 20 marks (score full 20/20 marks if methodology to be followed is clearly stated and fits well with the problem and perfectly feasible. score 16 marks if the student submission has all the requirements and fits the project problem but needs some improvements. score 8/20 marks if the project plan lacks an explanation of the to be followed methodology, and also if the researcher seems to lack any awareness of this methodology's limitations and possible solution to those. score 0/20 if methodology is not specified).  **end product** is 20 marks (score full points of 20/20 marks if end product to be realized. score 10/20 marks if end product is not specified but provide hints of what the end product is likely to be. score 0/20 if end product is not specified is not specified or deduced).  **Submission before deadline** is 20 marks (score full 20/20 marks if they write that they submitted before the deadline, and 16/20 marks if they wrote in their report that they exceeded deadline, and if they did not specify deadline in their report they score 0/20 marks).  *** Total Points: 0 out of 100

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 

#     elif "Software Design Specifications" in name:
#         return """**Clarity and Organization** is 25 marks (score full marks 25/25 marks if the work has Exceptional clarity and organization, and if Each section is well-structured, logically presented, and easy to follow, and if Information is presented in a reader-friendly manner with appropriate headings and formatting. score 15/25 if the work is Adequately organized, but improvements are needed. Some sections may be challenging to follow, and the overall flow could be enhanced with better structuring. score 5/25 if the work is Extremely disorganized, unclear and if The document is challenging to follow, and key information is buried or not easily discernible.). **Depth and Comprehensiveness** is 25 marks (score full marks 25/25 marks if the work has Exceptional depth and coverage of all aspects, and Provides a comprehensive understanding of the software design specifications with detailed descriptions for each element and All relevant components are thoroughly addressed. score 15/25 if the work is Adequate coverage, but lacking in some details. Most components are covered, but some areas may be insufficiently detailed or lack clarity. score 5/25 if the work is Minimal content provided, lacks essential information, and contains multiple inaccuracies. The understanding of the software design specifications is severely compromised). **Practicality and Feasibility** is 25 marks (score full marks 25/25 marks if the work Demonstrates a practical / feasible approach to software design and if its Strategies and plans outlined are highly realistic, considering potential challenges and constraints and if The design is well-aligned with the projects purpose and scope. score 15/25 if the work has Adequate practicality, but lack consideration for certain challenges, and  if The design is generally feasible, but some aspects may need further refinement to address potential issues. score 5/25 if the work is Impractical design with minimal feasibility considerations and if The design is not realistic, and key aspects may be unattainable or unworkable in practice.). **Problem & Design/Solution Fit** is 25 marks (score full marks 25/25 marks if the work Demonstrates a deep understanding of the problem domain, and the design aligns seamlessly with solving the identified problems and if The solution is well-crafted and tailored precisely to meet the requirements and scope of the project. score 15/25 if the work Adequately addresses the identified problems with an acceptable design/solution fit and if Some elements of the design may not fully align with certain aspects of the identified problems or may lack a comprehensive fit. score 5/25 if the work Fails to establish a clear connection between the identified problems and the proposed design/solution and if The design is not well-suited to address the key challenges, leading to a substantial mismatch.).

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 
    
#     elif "Software Requirements Specifications" in name:
#         return """**Content Accuracy and Completeness** is 25 marks (score full marks 25/25 marks if the work is Thorough and accurate coverage of all aspects and if Clear and comprehensive descriptions of the product overview, features, user classes, functional and non-functional requirements, external interfaces, and constraints and also if No critical information is missing. score 15/25 if the work showcase an Adequate coverage of the major components and if Some information may be lacking or not fully developed and also if Accuracy is generally good but may have a few noticeable errors or omissions. score 5/25 if the work contains Minimal content provided, lacks essential information, and contains multiple inaccuracies. The understanding of the software requirements is severely compromised.). **Clarity and Organization** is 25 marks (score full marks 25/25 marks if the work has Exceptional clarity and organization. Each section is well-structured, logically presented, and easy to follow. Information is presented in a reader-friendly manner with appropriate headings and formatting. score 15/25 if the work is Adequately organized, but improvements are needed. Some sections may be challenging to follow, and the overall flow could be enhanced with better structuring. score 5/25 if the work is Extremely disorganized and unclear. The document is challenging to follow, and key information is buried or not easily discernible.). **Detail and Insight** is 25 marks (score full marks 25/25 marks if the work Provides detailed insights into each aspect, going beyond the basic requirements, and if Demonstrates a deep understanding of software specifications, anticipating potential issues and dependencies. score 15/25 if the work contains Adequate details provided but lacks depth and if it Demonstrates a basic understanding of software specifications but may miss some nuances or potential issues. score 5/25 if the work contains Minimal details, lacks depth, and demonstrates a poor understanding of software specifications.). **Clarity and Measurability of Acceptance Criteria**  is 25 marks (score full marks 25/25 marks if the document includes clear, specific, and measurable acceptance criteria for each functional and non-functional requirement and also, if The criteria leave no room for ambiguity and provide a robust basis for evaluating the softwares compliance. score 15/25 if Acceptance criteria are present, but some lack specificity or measurability, While they contribute to understanding, improvements are needed to ensure a more precise evaluation. score 5/25 if the work has Little to no emphasis on acceptance criteria. Lack of clear, specific, and measurable criteria severely impacts the ability to evaluate the software requirements.)

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 
    
    
#     elif "W7- Project Assignment- Brainstorming- Convergence" in name:
#         return """**Time Management** is 10 marks (score full marks 10/10 marks if the work states that the Assignment was Submitted before the deadline. score 8/10 if the works states that the Assignment was Submitted max 2 days after the deadline.. score 6/10 if the works states that the Assignment was Submitted 3-7 days after the deadline. score 4/10 if the works states that that submission was More than 1 week late, that is, Assignment Submitted 8-14 days after the deadline. score 2/10 if the works states that the Assignment was Submitted more than 2 weeks after the deadline.).  **Understanding of Convergence** is 25 marks (score full marks 25/25 marks if The student thoroughly articulates the converging phase, explaining its role in narrowing down ideas to a feasible solution by systematically reducing options based on predefined criteria and if A clear distinction is made between the converging and diverging phases, demonstrating an advanced understanding of the purpose and process of each stage. score full marks 20/25 marks if The student explains the converging phase well, showing an understanding of how ideas are refined and selected and if Some minor details on the comparison with the diverging phase may be lacking, but overall, the explanation is well-structured. score full marks 20/25 marks if The student demonstrates only a vague understanding of the converging phase, failing to clearly distinguish it from the diverging phase. The explanation may be confused or incomplete. score full marks 20/25 marks if The student does not adequately explain the converging phase, showing little to no understanding of its role or how it contrasts with the diverging phase.).  **Converging Tools and Techniques** is 45 marks (score full marks 45/45 marks if The student identifies and applies multiple specific tools effectively to converge ideas, providing a clear rationale for how each tool helps narrow down options and if The answer demonstrates an advanced ability to critically evaluate the relevance of each technique in refining ideas for the project. score full marks 27/45 marks if The student discusses two or more tools and techniques for converging ideas, explaining how they helped in narrowing down ideas. Some tools may lack detailed justification, but the overall rationale for their selection is solid. score full marks 27/45 marks if The student identifies at least one tool or technique used to converge ideas but provides limited detail on how it was applied or how it helped refine the brainstormed ideas. The explanation is adequate but lacks depth. score full marks 18/45 marks if The student mentions tools or techniques for convergence but fails to explain how they were applied in the context of the project. The rationale for selecting these tools is weak or unclear. score full marks 9/45 marks if The student either fails to identify relevant tools for convergence or provides an inadequate explanation of their application and effectiveness.).  **Alignment with Project Goals** is 20 marks (score full marks 20/20 marks if The decision-making criteria are clearly articulated and demonstrate a strong alignment with both the overarching project goals and the specific user needs and if Each criterion directly supports achieving project success, reflecting a deep understanding of how the selected ideas address key project objectives and user challenges. score full marks 16/20 marks if The criteria reflect a solid understanding of the project goals, with most of the selected ideas aligning well with the intended outcomes and if Minor gaps exist in fully connecting all ideas to the user needs or project objectives, but the overall alignment remains robust. score full marks 12/20 marks if The student identifies at least one tool or technique used to converge ideas but provides limited detail on how it was applied or how it helped refine the brainstormed ideas and also if The explanation is adequate but lacks depth. score full marks 4/20 marks if The decision-making criteria are either absent or fail to address the project goals and user needs and if The ideas selected show no strategic alignment, undermining the overall effectiveness of the converging phase.).

# Format:
# Criteria         Full marks (20)                           16 marks                                 8 marks

# xyz                description of rubric                description of rubric            description of rubric        
# """ 
    
#     else:
#         return "correctness 10% and quality of solution 90%"




# def parse_ai_response(response_text):
#     """
#     Parse the AI-generated response to extract grade, feedback, and suggestions.

#     Args:
#         response_text (str): The response text from the AI.

#     Returns:
#         dict: A dictionary containing 'grade', 'feedback', and 'suggestions'.
#     """
#     result = {"grade": None, "feedback": "", "suggestions": ""}
    
#     # Extract grade
#     grade_match = re.search(r'Grade:\s*(\d{1,3})', response_text)
#     if grade_match:
#         result["grade"] = int(grade_match.group(1))
    
#     # Extract feedback and suggestions
#     feedback_match = re.search(r'Feedback:\s*(.*?)\s*Suggestions:', response_text, re.DOTALL)
#     suggestions_match = re.search(r'Suggestions:\s*(.*)', response_text, re.DOTALL)
    
#     if feedback_match:
#         result["feedback"] = feedback_match.group(1).strip()
#     if suggestions_match:
#         result["suggestions"] = suggestions_match.group(1).strip()
    
#     return result



# def get_ai_feedback(rubric, submission_text):
#     """
#     Generate AI-based feedback for a student's submission based on the provided rubric.

#     Args:
#         rubric (str): The grading rubric.
#         submission_text (str): The student's submission text.

#     Returns:
#         dict: A dictionary containing 'grade', 'feedback', 'suggestions', or 'error'.
#     """
#     # system_prompt = (
#     #     "You are an expert grading assistant. Analyze the student submission "
#     #     "strictly against the provided rubric. But do not Provide any numerical grade (0-100), just give detailed feedback without numerical grades "
#     #     "focusing on rubric criteria, and specific suggestions for improvement. Format your response as:\n"
#     #     "Feedback: [detailed feedback]\n"
#     #     "Suggestions: [concrete improvement suggestions]"
#     # )
    
#     system_prompt = """You are an expert grading assistant. Analyze the student submission 
#     strictly against the provided rubric. One can guage the students performance by a numerical grade (0-100) or (0-Total score stipulated on the rubric) derived from summing up each marks or points scored on rubrics, but please display detailed feedback only without including the numerical grade 
#     focusing on rubric criteria, and specific suggestions for improvement. Format your response as:
#     Grade: [numerical value that is determined by finding the cumulative sum of all marks (sum/Total score stipulated on the rubric) on each part of the rubric. Apply addition in mathematics]
#     Feedback: [provide feedback with each point expressing student performance based on the rubrics. include the point scored on each based on the rubrics e.g., 0/20]
#     Suggestions: [concrete actionable improvement suggestions]
#     When generating the 'Suggestions', please students adhere to these guidelines from mentor:
#     As a student mentor, What would you you tell the students to do to get a better score or result based on the rubrics, and also to improve their knowledge and skill
#     Include the Grade here. Grade: [numerical value (sum/Total score stipulated on the rubric, e.g 10/15 or 15/100 or 45/Total rubric score)]
#     """
    
    
#     user_prompt = f"RUBRIC CRITERIA:\n{rubric}\n\nSTUDENT SUBMISSION:\n{submission_text}\n\nYOUR EVALUATION:"
    
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.0,
#             max_tokens=1000
#         )
#         return parse_ai_response(response.choices[0].message['content'].strip())
#     except Exception as e:
#         return {"error": str(e)}
















def parse_ai_response(response_text):
    """
    Parse the AI-generated response to extract grade, feedback, and suggestions.
    Now includes total score at the bottom of suggestions.
    """
    result = {"grade": None, "feedback": "", "suggestions": ""}
    
    # Extract grade in X/Y format
    grade_match = re.search(r'Grade:\s*(\d+/\d+)', response_text)
    if grade_match:
        result["grade"] = grade_match.group(1)
    
    # Extract feedback and suggestions
    feedback_match = re.search(r'Feedback:\s*(.*?)\s*Suggestions:', response_text, re.DOTALL)
    suggestions_match = re.search(r'Suggestions:\s*(.*?)(\n\s*Score:)?\s*$', response_text, re.DOTALL)
    
    if feedback_match:
        result["feedback"] = feedback_match.group(1).strip()
    if suggestions_match:
        result["suggestions"] = suggestions_match.group(1).strip()
    
    # Add formatted score to suggestions
    if result["grade"]:
        result["suggestions"] += f"\n\nScore: {result['grade']}"
    
    return result

def get_ai_feedback(rubric, submission_text):
    """
    Generate AI-based feedback with enhanced scoring format
    """
    system_prompt = """You are an expert grading assistant. Analyze the student submission 
    strictly against the provided rubric. Format your response as:
    
    Grade: [sum/Total score from rubric (e.g., 12/15 or 85/100 and     This denominator of the grade is the total sum of the rubric scores)]
    Feedback: [Criterion-based feedback with individual scores]
    Suggestions: [Actionable improvement suggestions]
    When generating the 'Suggestions', please students adhere to these guidelines from mentor:
    As a student mentor, What would you you tell the students to do to get a better score or result based on the rubrics, and also to improve their knowledge and skill
    
    Guidelines:
    1. Calculate total score by summing rubric criterion points
    2. In Feedback, include per-criterion scores (e.g., "Structure: 4/5")
    3. Suggestions should focus on specific rubric improvements
    4. Maintain professional academic tone, yet human friendly response like a student mentor or facilitator
    """
    
    user_prompt = f"""RUBRIC:
{rubric}

SUBMISSION:
{submission_text}

EVALUATION:"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,  # Slightly higher temp for varied phrasing
            max_tokens=1200
        )
        return parse_ai_response(response.choices[0].message['content'].strip())
    except Exception as e:
        return {"error": str(e)}













def get_ai_feedback_student(rubric, submission_text):
    """
    Generate AI-based feedback for a student's submission based on the provided rubric.

    Args:
        rubric (str): The grading rubric.
        submission_text (str): The student's submission text.

    Returns:
        dict: A dictionary containing 'grade', 'feedback', 'suggestions', or 'error'.
    """
    system_prompt = (
        "Hello there! I'm your friendly grading assistant "
        "The feedback generated would prompt you to think more deeply, rather than just telling you what to do to fix your work.\n\n"
        "When providing feedback, please use this format:\n"
        "Feedback: [First I will povide you a detailed feedback of your submission based on the rubric, and next In a simple way, I will ask five (5) important questions for each rubrics in relations to your submission, and these questions will lead you to think of the best way to improve your work \]\n"
        "Suggestions: [concrete, five (5) actionable advice to help you improve but it will only be in a question format]\n\n"        
        """
        For instance, instead of giving a suggestion like "Enhance the Challenges in Defining the Problem section by offering more detailed explanations of how each challenge was overcome and the specific outcomes of those strategies."
        I Will suggest:
        "Your section on Challenges in Defining the Problem is insightful. How did you overcome each challenge? Adding more details on the steps you took and their outcomes will strengthen your analysis."
        """
        "Let's dive in and see how we can make your work even better!"
    )

    user_prompt = (
        f"RUBRIC CRITERIA:\n{rubric}\n\n"
        f"STUDENT SUBMISSION:\n{submission_text}\n\n"
        "YOUR EVALUATION:"
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=1000
        )
        return parse_ai_response(response.choices[0].message['content'].strip())
    except Exception as e:
        return {"error": str(e)}







# Modify the save_grading_record function in your utils/grading.py
def save_grading_record(record):
    """Save grading record to database with duplicate check and grade conversion"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert grade from fraction to percentage if needed
        if isinstance(record['grade'], str) and '/' in record['grade']:
            parts = record['grade'].split('/')
            if len(parts) == 2:
                try:
                    numerator = int(parts[0])
                    denominator = int(parts[1])
                    
                    if denominator == 100:
                        # Directly use numerator if denominator is 100
                        record['grade'] = numerator
                    else:
                        # Calculate percentage for other denominators
                        record['grade'] = round((numerator / denominator) * 100)
                except (ValueError, ZeroDivisionError):
                    raise ValueError("Invalid grade format. Use 'X/Y' or integer value")
        else:
            # Handle integer grades directly
            try:
                record['grade'] = int(record['grade'])
            except:
                raise ValueError("Grade must be in 'X/Y' format or integer value")

        # Rest of the duplicate check and insert logic remains the same
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM grading_records
                WHERE course_id = %s
                AND assignment = %s
                AND student = %s
                AND file = %s
                AND grade = %s
                AND feedback = %s
                AND suggestions = %s
                AND instructor_comment = %s
            )
        """, (
            record['course_id'],
            record['assignment'],
            record['student'],
            record['file'],
            record['grade'],
            record['feedback'],
            record['suggestions'],
            record['instructor_comment']
        ))
        
        exists = cursor.fetchone()[0]
        
        if exists:
            return 'duplicate'
        
        cursor.execute("""
            INSERT INTO grading_records 
            (course_id, assignment, student, file, grade, feedback, 
             suggestions, instructor_comment, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            record['course_id'],
            record['assignment'],
            record['student'],
            record['file'],
            record['grade'],
            record['feedback'],
            record['suggestions'],
            record['instructor_comment'],
            record['timestamp']
        ))
        conn.commit()
        return 'success'
    except Exception as e:
        conn.rollback()
        print(f"Database error: {str(e)}")
        return 'error'
    finally:
        cursor.close()
        conn.close()


# def save_grading_record(record):
#     """Save grading record to database with duplicate check"""
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Convert grade from fraction (e.g., "48/100") to just the numerator (48)
#         if isinstance(record['grade'], str) and '/' in record['grade']:
#             numerator = record['grade'].split('/')[0]  # Extract numerator
#             record['grade'] = int(numerator)  # Convert to integer
        
#         # Check for existing duplicate record (excluding timestamp)
#         cursor.execute("""
#             SELECT EXISTS(
#                 SELECT 1 FROM grading_records
#                 WHERE course_id = %s
#                 AND assignment = %s
#                 AND student = %s
#                 AND file = %s
#                 AND grade = %s
#                 AND feedback = %s
#                 AND suggestions = %s
#                 AND instructor_comment = %s
#             )
#         """, (
#             record['course_id'],
#             record['assignment'],
#             record['student'],
#             record['file'],
#             record['grade'],
#             record['feedback'],
#             record['suggestions'],
#             record['instructor_comment']
#         ))
        
#         exists = cursor.fetchone()[0]
        
#         if exists:
#             return 'duplicate'
        
#         # Insert new record if no duplicate found
#         cursor.execute("""
#             INSERT INTO grading_records 
#             (course_id, assignment, student, file, grade, feedback, 
#              suggestions, instructor_comment, timestamp)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """, (
#             record['course_id'],
#             record['assignment'],
#             record['student'],
#             record['file'],
#             record['grade'],
#             record['feedback'],
#             record['suggestions'],
#             record['instructor_comment'],
#             record['timestamp']
#         ))
#         conn.commit()
#         return 'success'
#     except Exception as e:
#         conn.rollback()
#         print(f"Database error: {str(e)}")
#         return 'error'
#     finally:
#         cursor.close()
#         conn.close()






def get_all_grading_data():
    """
    Retrieve all grading records from the database.

    Returns:
        pd.DataFrame: A DataFrame containing all grading records.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM grading_records")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Course ID", "Assignment", "Student", "File", "Grade", "Feedback", "Suggestions", "Timestamp"])
            return df
    except Exception as e:
        st.error(f"Error fetching grading data: {e}")
        return []
    finally:
        conn.close()


































def save_grading_record_student(record):
    """Save grading record to database with duplicate check"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for existing duplicate record (excluding timestamp)
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM student_grading_records
                WHERE course_id = %s
                AND assignment = %s
                AND student = %s
                AND file = %s
                AND feedback = %s
                AND suggestions = %s
                AND need_more_clarity_comment = %s
            )
        """, (
            record['course_id'],
            record['assignment'],
            record['student'],
            record['file'],
            record['feedback'],
            record['suggestions'],
            record['need_more_clarity_comment']
        ))
        
        exists = cursor.fetchone()[0]
        
        if exists:
            return 'duplicate'
        
        # Insert new record if no duplicate found
        cursor.execute("""
            INSERT INTO student_grading_records 
            (course_id, assignment, student, file, feedback, 
             suggestions, need_more_clarity_comment, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            record['course_id'],
            record['assignment'],
            record['student'],
            record['file'],
            record['feedback'],
            record['suggestions'],
            record['need_more_clarity_comment'],
            record['timestamp']
        ))
        conn.commit()
        return 'success'
    except Exception as e:
        conn.rollback()
        print(f"Database error: {str(e)}")
        return 'error'
    finally:
        cursor.close()
        conn.close()


def get_all_grading_data_student():
    """
    Retrieve all grading records from the database.

    Returns:
        pd.DataFrame: A DataFrame containing all grading records.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM student_grading_records")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Course ID", "Assignment", "Student", "File", "Feedback", "Suggestions", "need_more_clarity_comment"])
            return df
    except Exception as e:
        st.error(f"Error fetching grading data: {e}")
        return []
    finally:
        conn.close()







# utils/grading.py

def grade_submission(submission):
    """
    Process and grade a student's submission.

    Args:
        submission (dict): A dictionary containing submission details.

    Returns:
        dict: A dictionary containing the grading results.
    """
    # Example grading logic
    score = 0
    feedback = "Good effort."

    # Implement your grading logic here
    # For instance, evaluate the submission content and assign a score

    return {
        'score': score,
        'feedback': feedback
    }
    


         ## SYSTEM PROMPT
        # "Hello there! I'm your friendly grading assistant, here to help you understand your work better. "
        # "I'll review your submission based on the rubric provided and share detailed, supportive feedback with you. "
        # "Instead of giving a number grade, I'll focus on what you've done well and offer suggestions for improvement, "
        # "complete with examples and guiding questions to help you reflect on your work. "
        # "Think of me as your learning partner, here to provide insights and help you grow. "
        # "Also, if you see the word 'Overall' in any of my suggestions, I'll be rephrasing it to keep the tone personal and engaging,"
        # "The feedback generated for faculty should prompt students to think more deeply, rather than just telling them what to do.\n\n"
        # "When providing feedback, please use this format:\n"
        # "Feedback: [detailed feedback explaining your performance based on the rubric, including examples from your submission]\n"

        # "Suggestions: [concrete, actionable advice to help you improve]\n\n"
        # "Let's dive in and see how we can make your work even better!"
    
    # • Provide formative feedback that emphasizes developmental growth. Clearly state what the student did well and specify areas that need refinement (e.g., 'Consider restructuring this argument for clarity').
    # • Use guiding questions to encourage student reflection. For example, ask 'What evidence supports this claim?' or 'How might you expand this idea to include counterarguments?'
    # • Focus on process-oriented feedback by discussing the methodology and the steps taken, and ask questions such as, 'How might you address potential biases in your approach?'
    # • Offer actionable suggestions that guide revisions without giving away direct solutions. Encourage exploration of alternatives rather than spoonfeeding answers.
    # • Promote critical thinking by including open-ended prompts. Ask questions like 'What additional evidence would strengthen this section?' or 'Which aspects of your work align best with the assignment criteria and why?'
    # • Encourage self-assessment and reflective practices with prompts such as 'Based on this feedback, what changes will you make and why?' and 'What aspect of your work are you most confident about?'
    # • Use Socratic questioning to challenge assumptions and stimulate deeper analysis. For example, ask 'What assumptions are you making here? Are they valid?'
    # • Position yourself as a generative thinking partner by offering multiple perspectives and iterative improvement strategies. Suggest, 'Here are three perspectives on your argument. Which aligns best with your goals?'
    # • Incorporate scenario-based feedback where applicable, such as 'Imagine your audience is unfamiliar with this concept. How would you explain it in simpler terms?'
    # • Scaffold the complexity of your feedback by starting with simpler guidance and gradually introducing higher-order challenges as appropriate.
    # Provide your evaluation solely based on the provided rubric and submission. 
    # • Paraphrase the word 'Overall' in any statement if it is in the AI suggestion response
    
    
    
    
    

 
# def fetch_assignment_rubric(assignment_name):
#     """
#     Retrieve the grading rubric based on the assignment name.

#     Args:
#         assignment_name (str): The name of the assignment.

#     Returns:
#         str: The corresponding grading rubric.
#     """
#     rubrics = {
#         "Individual Assignment- Research & Discovery": "Correctness 10% and quality of solution 90%",
#         "Individual Assignment- Assumption Testing": "Correctness 10% and quality of solution 90%",
#         "Project Assignment- Brainstorming- Convergence": "Correctness 10% and quality of solution 90%",
#         "Project Assignment- Identify an Opportunity": "Correctness 10% and quality of solution 90%",
#         "Individual Assignment- 'What Is?' Stage": "Correctness 10% and quality of solution 90%",
#         "Project Plan": (
#             "**Effect on reader** is 20 points (score full 20 points if it ticks all boxes and has wow-factor. "
#             "Remove 8 points if it doesn't tick all but ticks the majority of the boxes and is also interesting to the reader. "
#             "Remove 16 points if it's off-topic and going nowhere, and it ticks a minority of the boxes), "
#             "**Project problem/idea** is 20 points (score full 20 points if the project idea is clearly stated and solves a real-life problem that is feasible, and is supported by three literature sources. "
#             "Remove 8 points if it has all of the requirements but does not reflect why the researcher wants to do the project. "
#             "Remove 16 points if the project idea is unclear, not a real-life problem, and is not feasible), "
#             "**Methodology** is 20 points (score full 20 points if the methodology to be followed is clearly stated, fits well with the problem, and is perfectly feasible. "
#             "Remove 8 points if the student submission has all the requirements and fits the project problem but needs some improvements. "
#             "Remove 16 points if the project plan lacks an explanation of the methodology to be followed, and also if the researcher seems to lack any awareness of this methodology's limitations and possible solutions to those), "
#             "**End product** is 20 marks. "
#             "**Submission before deadline** is 20 marks (score full 20 points if the student wrote in their report if they exceeded the deadline or not, and if they did not include it in their report they score 10 marks). "
#             "*** Total Points: 0 out of 100"
#         )
#     }
#     return rubrics.get(assignment_name, "Correctness 10% and quality of solution 90%")





def fetch_assignment_rubric(assignment_name):
    """
    Retrieve the grading rubric based on the assignment name.

    Args:
        assignment_name (str): The name of the assignment.

    Returns:
        str: The corresponding grading rubric.
    """
    rubrics = {
                 
  


         "Software Requirements Specifications": (
         """
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome
Content Accuracy and Completeness:
5 pts
Excellent
Thorough and accurate coverage of all aspects. Clear and comprehensive descriptions of the product overview, features, user classes, functional and non-functional requirements, external interfaces, and constraints. No critical information is missing.
4 pts
Very Good
Solid coverage of most aspects with minor gaps. Information is accurate and well-presented, but a few details could be more explicit or thorough.
3 pts
Satisfactory
Adequate coverage of the major components. Some information may be lacking or not fully developed. Accuracy is generally good but may have a few noticeable errors or omissions.
2 pts
Fair
Incomplete coverage with significant gaps. Several inaccuracies or missing details that impact the overall understanding of the software requirements.
1 pts
Poor
Minimal content provided, lacks essential information, and contains multiple inaccuracies. The understanding of the software requirements is severely compromised.
5 pts

This criterion is linked to a Learning Outcome
Clarity and Organization:
5 pts
Excellent
Exceptional clarity and organization. Each section is well-structured, logically presented, and easy to follow. Information is presented in a reader-friendly manner with appropriate headings and formatting.
4 pts
Very Good
Clear and well-organized with only minor improvements needed. The document is mostly easy to follow, but a few sections may benefit from better transitions or formatting.
3 pts
Satisfactory
Adequately organized, but improvements are needed. Some sections may be challenging to follow, and the overall flow could be enhanced with better structuring.
2 pts
Fair
Limited organization and clarity. The document lacks a clear structure, making it difficult for the reader to understand the relationships between different sections.
1 pts
Poor
Extremely disorganized and unclear. The document is challenging to follow, and key information is buried or not easily discernible.
5 pts

This criterion is linked to a Learning Outcome
Detail and Insight:
5 pts
Excellent
Provides detailed insights into each aspect, going beyond the basic requirements. Demonstrates a deep understanding of software specifications, anticipating potential issues and dependencies.
4 pts
Very Good
Provides thorough details with insightful commentary. Demonstrates a solid understanding of software requirements and may include thoughtful considerations.
3 pts
Satisfactory
Adequate details provided but lacks depth. Demonstrates a basic understanding of software specifications but may miss some nuances or potential issues.
2 pts
Fair
Limited details provided. The understanding of software requirements is superficial, with significant gaps in insight and analysis.
1 pts
Poor
Minimal details, lacks depth, and demonstrates a poor understanding of software specifications.
5 pts

This criterion is linked to a Learning Outcome
Clarity and Measurability of Acceptance Criteria:
5 pts
Excellent
The document includes clear, specific, and measurable acceptance criteria for each functional and non-functional requirement. The criteria leave no room for ambiguity and provide a robust basis for evaluating the software's compliance.
4 pts
Very Good
Acceptance criteria are well-defined for most requirements, but a few could benefit from additional specificity or measurability. Overall, they contribute to the clarity of the document.
3 pts
Satisfactory
Acceptance criteria are present, but some lack specificity or measurability. While they contribute to understanding, improvements are needed to ensure a more precise evaluation.
2 pts
Fair
Acceptance criteria are either missing or inadequately defined. The document lacks the necessary detail to assess the software's compliance effectively.
1 pts
Poor
Little to no emphasis on acceptance criteria. Lack of clear, specific, and measurable criteria severely impacts the ability to evaluate the software requirements.
5 pts
Total Points: 20
"""     
         ),

              
         
         
     "Project Proposal": (              
     """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
EFFECT ON READER:
5 pts
Excellent
Wow factor: persuasive, insightful. Ticks all the boxes. Well formatted. Perfect length.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
Keeps the reader interested. Ticks a majority of the boxes. Looks good. Acceptable length.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
Off topic. Going nowhere. Ticks a minority of the boxes. Looks a bit of a mess. Too short / long.
5 pts

This criterion is linked to a Learning Outcome
PROJECT PROBLEM / IDEA:
5 pts
Excellent
The project idea is clearly stated. It is a real-life problem that definitely can be solved. The project idea is feasible and can be completed within the time frame of the programme. It clearly reflects the reasons why the researcher wants to do this project (supported by three literature sources) and their ambition to make a difference to the three different audiences.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
The project idea is stated. It is a real-life problem that can be solved. The project idea seems feasible and can probably be completed within the time frame of the programme. It reflects the reasons why the researcher wants to do this project (supported by literature sources) and their ambition to make a difference to the three audiences.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
The project idea is unclear. It is not a real-life problem and/or cannot be solved. The project idea seems not feasible and can probably not be completed within the time frame of the programme. It does not reflect the reasons why the researcher wants to do this project (and is not supported by literature sources) and it remains unclear regarding their ambition to make a difference to the three audiences.
5 pts

This criterion is linked to a Learning Outcome
METHODOLOGY:
5 pts
Excellent
The methodology to be followed is clearly stated. It fits well with the problem. It suggests an advanced methodology and looks perfectly feasible given the capabilities and competencies of the researcher who seems clearly aware of limitations and possible solutions to those. The methodology related to research is clearly described and fits well with the organisational environment given the capabilities and competencies of the researcher who seems clearly aware of a variety of limitations and possible solutions to those.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
The methodology to be followed is clearly stated. However, the fit with the project problem or the level of sophistication needs some improvement. The researcher shows some awareness of this methodology’s limitations and possible solutions to those. The methodology related to research is described in some detail and seems to have a fit with the organisational environment given the capabilities and competencies of the researcher who seems aware of some of his own and the action research setup’s limitations and possible solutions to those.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
The project plan lacks an explanation of the to be followed methodology. The researcher seems to lack any awareness of this methodology’s limitations and possible solutions to those. The methodology related to research is not described in any detail and/or lacks a fit with the organisational environment given the capabilities and competencies of the researcher who doesn’t seem aware of some of his own and the research setup’s limitations and possible solutions to those.
5 pts

This criterion is linked to a Learning Outcome
END PRODUCT:
5 pts
Excellent
The proposed end product seems an excellent solution for the problem/ challenge. It involves a good level of sophistication. A prototype is presented.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
The proposed end product seems to solve the proposed problem. It involves a basic level of software engineering.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
The project plan lacks an explanation of the expected end product.
5 pts

This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--
Total Points: 20
"""
         ),    
         



        
        
        "Software Design Specifications": ( 
        
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Clarity and Organization:
5 pts
Excellent
Exceptional clarity and organization. Each section is well-structured, logically presented, and easy to follow. Information is presented in a reader-friendly manner with appropriate headings and formatting.
4 pts
Very Good
Clear and well-organized with only minor improvements needed. The document is mostly easy to follow, but a few sections may benefit from better transitions or formatting.
3 pts
Satisfactory
Adequately organized, but improvements are needed. Some sections may be challenging to follow, and the overall flow could be enhanced with better structuring.
2 pts
Fair
Limited organization and clarity. The document lacks a clear structure, making it difficult for the reader to understand the relationships between different sections.
1 pts
Poor
Extremely disorganized and unclear. The document is challenging to follow, and key information is buried or not easily discernible.
5 pts

This criterion is linked to a Learning Outcome
Depth and Comprehensiveness:
5 pts
Excellent
Exceptional depth and coverage of all aspects. Provides a comprehensive understanding of the software design specifications with detailed descriptions for each element. All relevant components are thoroughly addressed.
4 pts
Very Good
Solid coverage with minor improvements possible. Each section is well-detailed, but a few areas could benefit from additional depth or clarity to enhance overall comprehension.
3 pts
Satisfactory
Adequate coverage, but lacking in some details. Most components are covered, but some areas may be insufficiently detailed or lack clarity.
2 pts
Fair
Limited coverage with notable gaps. Several aspects are not adequately detailed, impacting the overall understanding of the software design specifications.
1 pts
Poor
Minimal content provided, lacks essential information, and contains multiple inaccuracies. The understanding of the software design specifications is severely compromised.
5 pts

This criterion is linked to a Learning Outcome
Practicality and Feasibility:
5 pts
Excellent
Demonstrates a practical and feasible approach to software design. Strategies and plans outlined are highly realistic, considering potential challenges and constraints. The design is well-aligned with the project's purpose and scope.
4 pts
Very Good
Presents a practical design with a few considerations for improvement. Most strategies are realistic, but some adjustments may be needed to enhance feasibility.
3 pts
Satisfactory
Adequate practicality, but may lack consideration for certain challenges. The design is generally feasible, but some aspects may need further refinement to address potential issues.
2 pts
Fair
Limited practicality, with significant gaps in feasibility considerations. The design may not fully account for potential challenges, impacting its overall feasibility.
1 pts
Poor
Impractical design with minimal feasibility considerations. The design is not realistic, and key aspects may be unattainable or unworkable in practice.
5 pts

This criterion is linked to a Learning Outcome
Problem & Design/Solution Fit:
5 pts
Excellent
Demonstrates a deep understanding of the problem domain, and the design aligns seamlessly with solving the identified problems. The solution is well-crafted and tailored precisely to meet the requirements and scope of the project.
4 pts
Very Good
Shows a strong connection between the identified problems and the proposed design/solution. The design effectively addresses the key challenges but may have minor areas that could be more closely aligned.
3 pts
Satisfactory
Adequately addresses the identified problems with an acceptable design/solution fit. Some elements of the design may not fully align with certain aspects of the identified problems or may lack a comprehensive fit.
2 pts
Fair
Demonstrates a partial understanding of the problem domain, and the design/solution fit is limited. Significant gaps exist between the identified problems and the proposed design, impacting the overall alignment.
1 pts
Poor
Fails to establish a clear connection between the identified problems and the proposed design/solution. The design is not well-suited to address the key challenges, leading to a substantial mismatch.
5 pts
Total Points: 20
"""
        ),
        
        
        
        
        
        "Project Plan": (             
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
EFFECT ON READER:
5 pts
Excellent
Wow factor: persuasive, insightful. Ticks all the boxes. Well formatted. Perfect length.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
Keeps the reader interested. Ticks a majority of the boxes. Looks good. Acceptable length.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
Off topic. Going nowhere. Ticks a minority of the boxes. Looks a bit of a mess. Too short / long.
5 pts

This criterion is linked to a Learning Outcome
PROJECT PROBLEM / IDEA:
5 pts
Excellent
The project idea is clearly stated. It is a real-life problem that definitely can be solved. The project idea is feasible and can be completed within the time frame of the programme. It clearly reflects the reasons why the researcher wants to do this project (supported by three literature sources) and their ambition to make a difference to the three different audiences.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
The project idea is stated. It is a real-life problem that can be solved. The project idea seems feasible and can probably be completed within the time frame of the programme. It reflects the reasons why the researcher wants to do this project (supported by literature sources) and their ambition to make a difference to the three audiences.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
The project idea is unclear. It is not a real-life problem and/or cannot be solved. The project idea seems not feasible and can probably not be completed within the time frame of the programme. It does not reflect the reasons why the researcher wants to do this project (and is not supported by literature sources) and it remains unclear regarding their ambition to make a difference to the three audiences.
5 pts

This criterion is linked to a Learning Outcome
METHODOLOGY:
5 pts
Excellent
The methodology to be followed is clearly stated. It fits well with the problem. It suggests an advanced methodology and looks perfectly feasible given the capabilities and competencies of the researcher who seems clearly aware of limitations and possible solutions to those. The methodology related to research is clearly described and fits well with the organisational environment given the capabilities and competencies of the researcher who seems clearly aware of a variety of limitations and possible solutions to those.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
The methodology to be followed is clearly stated. However, the fit with the project problem or the level of sophistication needs some improvement. The researcher shows some awareness of this methodology’s limitations and possible solutions to those. The methodology related to research is described in some detail and seems to have a fit with the organisational environment given the capabilities and competencies of the researcher who seems aware of some of his own and the action research setup’s limitations and possible solutions to those.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
The project plan lacks an explanation of the to be followed methodology. The researcher seems to lack any awareness of this methodology’s limitations and possible solutions to those. The methodology related to research is not described in any detail and/or lacks a fit with the organisational environment given the capabilities and competencies of the researcher who doesn’t seem aware of some of his own and the research setup’s limitations and possible solutions to those.
5 pts

This criterion is linked to a Learning Outcome
END PRODUCT:
5 pts
Excellent
The proposed end product seems an excellent solution for the problem/ challenge. It involves a good level of sophistication. A prototype is presented.
4 pts
Very Good
Features of band 3 and 5
3 pts
Satisfactory
The proposed end product seems to solve the proposed problem. It involves a basic level of software engineering.
2 pts
Fair
Features of band 1 and 3
1 pts
Poor
The project plan lacks an explanation of the expected end product.
5 pts

This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--
Total Points: 20
"""
        ),
       
         
          
       
        "W1 Individual Assignment- Identify an Opportunity": (            
         
"""
Criteria	Ratings	Pts
This criterion is linked to a Learning OutcomeTime Management
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning OutcomeCriteria 1: Understanding of Design Thinking Process
Learning Outcome 3.2.a. Familiarity of Design Thinking Framework
20 pts
Excellent
Demonstrates a comprehensive understanding of the Design Thinking process, including its origins, key principles, and contemporary applications. Provides insightful examples of its use in innovation work, clearly articulating the value it brings.
16 pts
Very Good
Shows a solid grasp of the Design Thinking process and its applications. Examples are relevant but may lack depth or insight into the broader context.
12 pts
Satisfactory
Provides a basic understanding of the Design Thinking process. Examples are present but may be superficial or lack clear connection to the principles discussed.
8 pts
Fair
Demonstrates limited understanding of the Design Thinking process. Examples are vague or unrelated, showing minimal connection to the principles.
4 pts
Poor
Shows little to no understanding of the Design Thinking process. Lacks examples or any clear articulation of its principles and applications.
20 pts

This criterion is linked to a Learning OutcomeCriteria 2: Distinction between Design Thinking and Engineering Thinking
Learning Outcome 3.3.a. Understanding Organisational Conditions for Innovation
25 pts
Excellent
Clearly articulates the differences between Design Thinking and Engineering Thinking with a well-developed example from their project. Demonstrates deep understanding of how these approaches might clash and provides thoughtful reflections on managing this tension.
20 pts
Satisfactory
Identifies basic differences between Design Thinking and Engineering Thinking. Example from the project is provided but lacks detail or reflection.
15 pts
Satisfactory
Identifies basic differences between Design Thinking and Engineering Thinking. Example from the project is provided but lacks detail or reflection.
10 pts
Fair
Provides a limited explanation of the differences between Design Thinking and Engineering Thinking. Example is vague or not well connected to the project.
5 pts
Poor
Shows minimal understanding of the differences between Design Thinking and Engineering Thinking. Lacks a coherent example or reflection.
25 pts

This criterion is linked to a Learning OutcomeCriteria 3: Application of Design Thinking in the Chosen Project
Learning Outcome 5.2.b. Strategic Guidance
25 pts
Excellent
Provides a detailed and thoughtful plan for applying Design Thinking in the chosen project. Clearly articulates the rationale behind project choice and how Design Thinking will be integrated.
20 pts
Satisfactory
Outlines a solid plan for using Design Thinking in the project. Rationale for project choice is clear, but details on application may lack some depth.
15 pts
Satisfactory
Describes a basic plan for using Design Thinking in the project. Rationale is present but not thoroughly explained.
10 pts
Fair
Offers a limited plan for applying Design Thinking in the project. Rationale for project choice is unclear or poorly articulated.
5 pts
Poor
Shows minimal thought in planning for the use of Design Thinking in the project. Lacks clear rationale or integration plan.
25 pts

This criterion is linked to a Learning OutcomeCriteria 4: Reflection on Personal Excitement and Challenges
Learning Outcome 5.2.c. Emerging as a Trusted Leader
20 pts
Excellent
Provides a deeply reflective and insightful account of personal excitement and anticipated challenges. Demonstrates a strong awareness of personal growth opportunities and potential obstacles in the Design Thinking process.
16 pts
Good
Reflects well on personal excitement and challenges. Shows good awareness of growth opportunities and obstacles, though reflections may lack some depth.
12 pts
Satisfactory
Offers basic reflections on personal excitement and challenges. Awareness of growth opportunities and obstacles is present but not deeply explored.
8 pts
Fair
Provides limited reflection on personal excitement and challenges. Awareness of personal growth opportunities and obstacles is minimal.
4 pts
Poor
Shows minimal reflection on personal excitement and challenges. Lacks awareness of personal growth opportunities or obstacles.
20 pts

Total Points: 100
"""      
       ),
   
   
                       

   
       
       
        "W1- Project Assignment- Identify an Opportunity": (              
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Criteria 1: Understanding of Design Thinking Process:
Learning Outcome 
3.2.a. Familiarity of Design Thinking Framework:
20 pts
Excellent
Demonstrates a comprehensive understanding of the Design Thinking process, including its origins, key principles, and contemporary applications. Provides insightful examples of its use in innovation work, clearly articulating the value it brings.
16 pts
Very Good
Shows a solid grasp of the Design Thinking process and its applications. Examples are relevant but may lack depth or insight into the broader context.
12 pts
Satisfactory
Provides a basic understanding of the Design Thinking process. Examples are present but may be superficial or lack clear connection to the principles discussed.
8 pts
Fair
Demonstrates limited understanding of the Design Thinking process. Examples are vague or unrelated, showing minimal connection to the principles.
4 pts
Poor
Shows little to no understanding of the Design Thinking process. Lacks examples or any clear articulation of its principles and applications.
20 pts

This criterion is linked to a Learning Outcome
Criteria 2: Distinction between Design Thinking and Engineering Thinking:
Learning Outcome 
3.3.a. Understanding Organisational Conditions for Innovation:
25 pts
Excellent
Clearly articulates the differences between Design Thinking and Engineering Thinking with a well-developed example from their project. Demonstrates deep understanding of how these approaches might clash and provides thoughtful reflections on managing this tension.
20 pts
Satisfactory
Identifies basic differences between Design Thinking and Engineering Thinking. Example from the project is provided but lacks detail or reflection.
15 pts
Satisfactory
Identifies basic differences between Design Thinking and Engineering Thinking. Example from the project is provided but lacks detail or reflection.
10 pts
Fair
Provides a limited explanation of the differences between Design Thinking and Engineering Thinking. Example is vague or not well connected to the project.
5 pts
Poor
Shows minimal understanding of the differences between Design Thinking and Engineering Thinking. Lacks a coherent example or reflection.
25 pts

This criterion is linked to a Learning Outcome
Criteria 3: Application of Design Thinking in the Chosen Project:
Learning Outcome 
5.2.b. Strategic Guidance:
25 pts
Excellent
Provides a detailed and thoughtful plan for applying Design Thinking in the chosen project. Clearly articulates the rationale behind project choice and how Design Thinking will be integrated.
20 pts
Satisfactory
Outlines a solid plan for using Design Thinking in the project. Rationale for project choice is clear, but details on application may lack some depth.
15 pts
Satisfactory
Describes a basic plan for using Design Thinking in the project. Rationale is present but not thoroughly explained.
10 pts
Fair
Offers a limited plan for applying Design Thinking in the project. Rationale for project choice is unclear or poorly articulated.
5 pts
Poor
Shows minimal thought in planning for the use of Design Thinking in the project. Lacks clear rationale or integration plan.
25 pts

This criterion is linked to a Learning Outcome
Criteria 4: Reflection on Personal Excitement and Challenges:
Learning Outcome 
5.2.c. Emerging as a Trusted Leader:
20 pts
Excellent
Provides a deeply reflective and insightful account of personal excitement and anticipated challenges. Demonstrates a strong awareness of personal growth opportunities and potential obstacles in the Design Thinking process.
16 pts
Good
Reflects well on personal excitement and challenges. Shows good awareness of growth opportunities and obstacles, though reflections may lack some depth.
12 pts
Satisfactory
Offers basic reflections on personal excitement and challenges. Awareness of growth opportunities and obstacles is present but not deeply explored.
8 pts
Fair
Provides limited reflection on personal excitement and challenges. Awareness of personal growth opportunities and obstacles is minimal.
4 pts
Poor
Shows minimal reflection on personal excitement and challenges. Lacks awareness of personal growth opportunities or obstacles.
20 pts
Total Points: 100
"""
        ),
        



   
    
        "W2- Project Assignment- Design Brief": (   
        """
Criteria	Ratings	Pts
Time Management:
view longer description
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
Points
/ 10 pts


Project Description:
view longer description
20 pts
Excellent
The project description is precise, clearly articulating the business problem or opportunity with a deep understanding of user needs. It effectively encapsulates the essence of the project in a way that is both engaging and informative, reflecting empathetic insight into the users' context.
16 pts
Very Good
The project description is clear and relevant, providing a good overview of the business problem or opportunity. There is a strong connection to user needs, though some elements could be more deeply explored or articulated.
12 pts
Satisfactory
The project description adequately identifies the business problem or opportunity but lacks depth in understanding user needs. It may be somewhat generic or miss key nuances that would make it more compelling.
8 pts
Fair
The project description is vague or incomplete, offering a limited understanding of the business problem or opportunity. It shows minimal consideration of user needs, reducing its overall effectiveness.
4 pts
Poor
The project description is unclear, irrelevant, or fails to address the business problem or opportunity in a meaningful way. There is little to no consideration of user needs.
Points
/ 20 pts


Scope:
view longer description
20 pts
Excellent
The scope is clearly defined with well-articulated boundaries, showing a comprehensive understanding of what is within and outside the project's scope. Constraints are thoughtfully considered, ensuring that the project remains feasible while addressing critical challenges.
16 pts
Very Good
The scope is well defined, with clear boundaries and constraints that are appropriate for the project. There is a good understanding of what is included, though some constraints could be more clearly articulated.
12 pts
Satisfactory
The scope is defined, but there may be some ambiguity or lack of clarity in what is included and excluded. Constraints are identified but may not be fully explored or integrated into the project plan.
8 pts
Fair
The scope is vague or incomplete, with unclear boundaries and poorly defined constraints. This lack of clarity may lead to challenges in project execution or misalignment with project goals.
4 pts
Poor
The scope is either not defined or is extremely unclear, with no consideration of boundaries or constraints. This significantly undermines the feasibility and focus of the project.
Points
/ 20 pts


User and Stakeholders:
view longer description
20 pts
Excellent
The identification of users and stakeholders is thorough and specific, reflecting a deep understanding of their roles, needs, and impacts on the project. The importance of each group is clearly articulated, demonstrating a strong connection to the project’s success.
16 pts
Very Good
Users and stakeholders are identified with reasonable specificity and relevance. Their roles and importance to the project are well explained, though some details might be further refined or explored.
12 pts
Satisfactory
The identification of users and stakeholders is adequate but may lack specificity or depth. The rationale for their importance is somewhat generic, with limited exploration of their roles.
8 pts
Fair
Users and stakeholders are identified in a broad and nonspecific manner. The explanation of their roles and importance is weak, showing little understanding of their impact on the project.
4 pts
Poor
Users and stakeholders are poorly identified or irrelevant to the project. Their roles and importance are either not explained or inadequately addressed, significantly weakening the project’s foundation.
Points
/ 20 pts


Exploration Questions:
view longer description
20 pts
Excellent
Exploration questions are insightful, focused, and clearly designed to uncover critical information about user behavior, needs, and motivations. The questions demonstrate a deep curiosity and strategic intent to inform the design process and drive meaningful insights.
16 pts
Very Good
Exploration questions are well crafted and relevant, aimed at uncovering important user information. They reflect a solid understanding of the design process, though there may be opportunities to sharpen their focus or depth.
12 pts
Satisfactory
Exploration questions are appropriate but may be somewhat generic or lack depth. They are likely to yield useful information, but they do not fully capitalize on the opportunity to deeply understand user needs and behaviors.
8 pts
Fair
Exploration questions are basic or lack focus, offering limited potential to uncover meaningful user insights. They may be too broad or too narrow, reducing their effectiveness in informing the design process.
4 pts
Poor
Exploration questions are poorly formulated, irrelevant, or superficial, offering little to no value in understanding user needs or informing the design process.
Points
/ 20 pts


Expected Outcomes and Success Metrics:
view longer description
10 pts
Excellent
The expected outcomes are clearly articulated, showing a strong alignment with the project’s objectives and potential impact. Success metrics are specific, measurable, and well-suited to assess the effectiveness of the project, providing a clear pathway for evaluating success.
8 pts
Very Good
The expected outcomes are well stated and generally align with the project’s goals. Success metrics are appropriate and relevant, though they may lack some specificity or comprehensiveness in capturing the project’s impact.
6 pts
Satisfactory
The expected outcomes are identified but may be somewhat generic or vague. Success metrics are present but may not fully capture the project's effectiveness or impact.
4 pts
Fair
The expected outcomes are poorly articulated or lack a clear connection to the project’s goals. Success metrics are either vague or insufficient to meaningfully measure success.
2 pts
Poor
The expected outcomes are unclear, irrelevant, or disconnected from the project’s goals. Success metrics are either absent or inadequate, offering no viable means to assess the project’s success.
Points
/ 10 pts

Total Points: 0 out of 100
"""
         ),
    
   
   
   
   
        
        "W2- Individual Assignment- Framing a Problem": (             
        """
Criteria	Ratings	Pts
This criterion is linked to a Learning Outcome
Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Impact of Problem-Framing on Project Direction:
This is related to Q1
Learning Outcome 
1.2.c: Insight-Driven Problem Framing:
30 pts
Excellent
The reflection provides a comprehensive and insightful analysis of how problem-framing significantly influenced the project’s direction, showcasing a deep understanding of the connection between problem definition and subsequent design decisions. The response clearly illustrates how problem-framing led to innovative opportunities within the project.
24 pts
Very Good
The analysis effectively explains the impact of problem-framing on the project’s direction, demonstrating a solid grasp of the subject. The response identifies some innovative outcomes that resulted from framing the problem but lacks the depth or breadth seen in higher-level responses.
15 pts
Satisfactory
The reflection provides a basic understanding of how problem-framing influenced the project’s direction. The connection between problem framing and design outcomes is mentioned but not explored in detail.
9 pts
Fair
The reflection shows limited understanding of how problem-framing influenced the project. The response is vague, with little evidence of how the framing affected the direction of the design thinking process.
0 pts
Poor
The reflection lacks clarity and does not adequately address the influence of problem-framing on the project. There is minimal to no connection made between the framing and the project’s outcomes.
30 pts

This criterion is linked to a Learning Outcome
Challenges in Defining the Problem and Resolution Approaches:
This is related to Q2
Learning Outcome 
1.3.a: Analyzing Research Findings:
20 pts
Excellent
The response offers a thorough and insightful discussion of the challenges faced in defining the problem, highlighting complex issues such as biases and assumptions. The strategies used to address these challenges are well-articulated, showing a clear, evidence-based approach.
16 pts
Very Good
The response discusses the challenges encountered in problem definition, with a clear explanation of the strategies employed to overcome them. There is a good understanding of biases and assumptions, though the analysis could be more detailed.
10 pts
Satisfactory
The reflection identifies basic challenges in defining the problem and mentions how they were addressed, but lacks depth. The response touches on biases and assumptions but does not explore them comprehensively.
6 pts
Fair
The response identifies a few challenges in problem definition but provides limited detail on how they were resolved. There is little consideration of biases and assumptions, indicating a superficial understanding.
0 pts
Poor
The response fails to adequately identify challenges or strategies used to address them. There is no meaningful discussion of biases, assumptions, or other complexities in problem definition.
20 pts

This criterion is linked to a Learning Outcome
Effectiveness of the Design Brief:
This is related to Q3
Learning Outcome 
3.1.b: Contemporary Significance:
20 pts
Excellent
The reflection provides a nuanced evaluation of the design brief's effectiveness in guiding the project, identifying its strengths and limitations with clarity. The analysis is well-supported by examples from the project, demonstrating a strong understanding of how a well-crafted design brief shapes project outcomes.
16 pts
Very Good
The reflection evaluates the design brief effectively, noting key strengths and limitations. While the analysis is solid, it could benefit from deeper insight or more comprehensive examples to illustrate the points made.
10 pts
Satisfactory
The reflection offers a basic evaluation of the design brief, acknowledging its role in guiding the project. The analysis is somewhat superficial, with general observations rather than specific examples or insights.
6 pts
Fair
The reflection provides a limited evaluation of the design brief, focusing more on the brief’s shortcomings than its strengths. The discussion is vague and lacks supporting examples or in-depth analysis.
0 pts
Poor
The reflection does not adequately evaluate the design brief's effectiveness. The response is unclear or off-topic, with little to no critical analysis of the brief's role in the project.
20 pts

This criterion is linked to a Learning Outcome
Strategies for Improved Problem-Framing and Design Brief Creation:
This is related to Q4
Learning Outcome 
1.2.b: Sensing Data-Driven User Needs:
20 pts
Excellent
The response proposes advanced, practical strategies for improving problem-framing and design brief creation in future projects. The suggestions are clearly rooted in the experiences and insights gained during the current project and show a strong ability to prioritize user needs and project goals.
16 pts
Very Good
The response provides solid strategies for improving future problem-framing and design briefs, with clear connections to the current project. The suggestions are practical but might lack the innovative thinking or depth required for an excellent rating.
10 pts
Satisfactory
The reflection offers some useful strategies for future improvement but lacks detail or specificity. The response is practical, though somewhat generic and not fully tailored to the specific challenges of the current project.
6 pts
Fair
The reflection provides limited strategies for future improvement, with vague or underdeveloped ideas. The response lacks a strong connection to the current project, indicating a superficial approach to learning from experience.
0 pts
Poor
The reflection fails to offer meaningful strategies for future improvement. The suggestions are either irrelevant or so vague that they do not demonstrate a clear understanding of how to enhance problem-framing or design brief creation.
20 pts
Total Points: 100
"""
        ),
       



         
        "W3- Project Assignment- Make Your Plans": (     
         """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning OutcomeClarity and Feasibility of Planned Activities
This is based on the Project Plan
Learning Outcome 
5.2.c Emerging as a Trusted Leader:
30 pts
Excellent
The project plan clearly outlines a detailed sequence of activities that are logically structured and demonstrate a thorough understanding of the project’s scope. The plan is adaptable, reflecting awareness of potential changes and uncertainties in the project lifecycle.
24 pts
Very Good
The project plan outlines a well-organized sequence of activities, though minor adjustments may be needed for better clarity or feasibility. The plan acknowledges uncertainties but could benefit from more detailed contingency considerations.
18 pts
Satisfactory
The project plan includes a basic sequence of activities that are generally clear, though some steps may lack specificity or appear overly ambitious without adequate contingency plans.
12 pts
Fair
The project plan presents an incomplete or poorly structured sequence of activities, with significant gaps in feasibility and insufficient consideration of potential changes.
6 pts
Poor
The project plan is unclear, with an illogical or incoherent sequence of activities, lacking any adaptability to project changes or uncertainties.
30 pts

This criterion is linked to a Learning OutcomeIdentification and Engagement Strategy for Stakeholders
This is based on the People Plan
Learning Outcome: 
5.1.a: Establishing a Working Client Relationship:
30 pts
Excellent
The people plan thoroughly identifies all relevant stakeholders, detailing their relationships to the project and specific roles. The engagement strategy is well-developed, clearly outlining how to secure support and communicate effectively with each stakeholder.
24 pts
Very Good
The people plan identifies most key stakeholders with clear roles and relationships. The engagement strategy is solid but may lack depth in addressing how to manage potential stakeholder challenges.
18 pts
Satisfactory
The people plan identifies the primary stakeholders with general roles and relationships. The engagement strategy is basic and might miss out on specific approaches for effective stakeholder management.
12 pts
Fair
The people plan only identifies some stakeholders, with vague or unclear roles and relationships. The engagement strategy is underdeveloped, leaving significant gaps in how to ensure stakeholder involvement.
6 pts
Poor
The people plan fails to identify key stakeholders or their roles, and lacks any coherent engagement strategy, jeopardizing the project's success.
30 pts

This criterion is linked to a Learning OutcomeComprehensiveness and Relevance of Research Strategy
This is based on the Research Plan
Learning Outcome: 
1.2.a Employ Research Triangulation:
30 pts
Excellent
The research plan is comprehensive, with well-defined research questions, a clear target population, and an appropriate number of interviews. It demonstrates a robust strategy for gathering and triangulating data, ensuring all relevant topics are explored thoroughly.
24 pts
Very Good
The research plan is detailed and covers the key research questions and target population, but could be slightly enhanced by refining the data gathering or triangulation strategy.
18 pts
Satisfactory
The research plan addresses the main research questions and target population but may lack depth in certain areas or provide insufficient details on data gathering and triangulation strategies.
12 pts
Fair
The research plan is underdeveloped, missing important research questions or failing to adequately define the target population. The data gathering strategy is weak, and triangulation is not clearly addressed.
6 pts
Poor
The research plan is inadequate, lacking clear research questions, an identifiable target population, or any coherent strategy for data gathering and analysis, severely limiting the project's foundation.
30 pts
Total Points: 100
"""
  
     ),
      
  
        
        
        "W3- Individual Assignment- Planning": (            
        """
Criteria	Ratings	Pts
This criterion is linked to a Learning OutcomeTime Management
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts
This criterion is linked to a Learning OutcomeStakeholder Prioritization and Effectiveness
This is related to Q1

Learning Outcome 5.1.a - Establishing a Working Client Relationship
30 pts
Excellent
The prioritization of stakeholders is based on a well-reasoned and strategic analysis, demonstrating a deep understanding of stakeholder roles and project goals. The approach is innovative and highly likely to be effective in practice.
24 pts
Very Good
The stakeholder prioritization is logical and mostly well-reasoned, with minor areas for improvement in strategic alignment. The approach is sound and likely to be effective.
18 pts
Satisfactory
The prioritization shows a basic understanding of stakeholder roles but may lack depth or full alignment with project goals. The approach is somewhat effective but could benefit from further refinement.
12 pts
Fair
The stakeholder prioritization is weak or unclear, with limited justification and weak alignment with project goals. The approach is unlikely to be fully effective.
6 pts
Poor
The prioritization lacks coherence and justification, showing little understanding of stakeholder roles or project goals. The approach is ineffective.
30 pts
This criterion is linked to a Learning OutcomeStructuring Engagement and Research Through Stakeholder Questions
This is related to Q2

Learning Outcome 5.1.b - Employing Clear Client Communication
30 pts
Excellent
The formulation of stakeholder questions is insightful, strategically structured, and closely aligned with research objectives and project goals. The questions effectively guide the engagement and research process.
24 pts
Very Good
The questions are well-formulated and structured with minor areas for improvement. The approach is mostly aligned with research objectives and effectively supports engagement.
18 pts
Satisfactory
The questions are adequately structured but may lack depth or full alignment with research objectives. The approach is moderately effective in guiding engagement.
12 pts
Fair
The questions are loosely structured and may not fully support research objectives or engagement goals. The approach is unlikely to be highly effective.
6 pts
Poor
The questions lack structure and coherence, failing to support the research objectives or engagement effectively. The approach is ineffective.
30 pts
This criterion is linked to a Learning OutcomeAdaptability and Embracing Uncertainty in Project Planning
This is related to Q3 & Q4

Learning Outcome 3.2.c - Comfort in Design Thinking Ambiguity
30 pts
Excellent
The reflection demonstrates a high level of confidence and preparedness for adapting to changes and managing uncertainty. Clear and proactive steps are outlined for harnessing change and embracing the iterative nature of design thinking.
24 pts
Very Good
The reflection shows solid confidence and readiness to adapt, with a well-considered approach to managing uncertainty. Minor improvements could enhance the effectiveness of the plan.
18 pts
Satisfactory
The reflection demonstrates a basic understanding of the need for adaptability and managing uncertainty, but the approach may lack depth or specificity. Preparedness is moderate.
12 pts
Fair
The reflection shows limited confidence in adaptability, with vague or incomplete strategies for managing uncertainty. The approach is reactive rather than proactive.
6 pts
Poor
The reflection lacks a coherent plan for adapting to changes or managing uncertainty, showing little understanding of the importance of flexibility in design thinking. The approach is ineffective.
30 pts
Total Points: 100
"""

          ),
        
        

   
    
        "W4- Individual Assignment- Research & Discovery": ( 
        """
Criteria	Ratings	Pts
Time Management
view longer description
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline
Points
/ 10 pts

Understanding of User Needs and Challenges
view longer description
60 pts
Excellent
The reflection demonstrates a comprehensive understanding of user needs, effectively integrating insights from personas, ethnographic interviews, and the "Jobs to be Done" framework. Challenges encountered during interviews are thoughtfully addressed with clear, creative solutions that enhance the overall design process.
48 pts
Very Good
The reflection shows a strong understanding of user needs and addresses challenges encountered during interviews. Solutions are practical and contribute to a deeper understanding of the design process, though there may be room for more creative or detailed approaches.
36 pts
Satisfactory
The reflection indicates an adequate understanding of user needs with basic application of insights from interviews and frameworks. Challenges are identified with some solutions offered, though they may lack depth or specificity.
24 pts
Fair
The reflection provides a limited understanding of user needs and only briefly touches on challenges during interviews. Solutions are minimal or unclear, and the connection to the design process is weak.
12 pts
Poor
The reflection fails to demonstrate a clear understanding of user needs, with little to no analysis of challenges or effective solutions. There is little connection to the overall design process.
Points
/ 60 pts

Evolution of Problem Perspective and Future Design Process
view longer description
30 pts
Excellent
The reflection provides a deep and thoughtful analysis of how the problem perspective has evolved through design research, with clear, forward-thinking implications for future problem-solving approaches. The student shows a strong ability to transform challenges into opportunities for innovation.
24 pts
Very Good
The reflection effectively discusses the evolution of the problem perspective with relevant insights into future design processes. The approach to transforming problems into opportunities is evident but could benefit from more detailed analysis.
18 pts
Satisfactory
The reflection shows a general understanding of how the problem perspective has changed, with some implications for future work. The transformation of problems into opportunities is addressed but not deeply explored.
12 pts
Fair
The reflection mentions changes in the problem perspective but lacks depth in analysis and future implications. The connection to transforming problems into opportunities is weak or unclear.
6 pts
Poor
The reflection does not adequately discuss the evolution of the problem perspective or its future implications. There is little to no consideration of transforming problems into opportunities.
Points
/ 30 pts

Total Points: 0 out of 100
"""    
       ),    

   
   
      
    
        "W4- Project Assignment- Interview, JTBD & Personas": (   
         """Criteria	Ratings  	Pts

Time Management:
view longer description
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
Points
/ 10 pts

Quality of User Interviews and Data Collection:
view longer description
30 pts
Excellent
The student effectively conducts in-depth interviews with well-structured questions that elicit rich qualitative data. The data clearly reflects a deep understanding of the user’s needs, desires, and pain points, with empathy consistently applied throughout.
24 pts
Very Good
The student conducts interviews that gather meaningful data, with most questions well-structured. There is good evidence of understanding user needs, though some aspects of empathy mapping could be more thoroughly developed.
18 pts
Satisfactory
The interviews cover the basics, but the questions may lack depth or fail to fully uncover key user needs. Empathy is applied, but inconsistently or superficially.
12 pts
Fair
The interviews are minimally effective, with poorly structured questions that result in limited or shallow data. The application of empathy is weak, leading to an incomplete understanding of user needs.
6 pts
Poor
The interviews are poorly conducted with little to no structure, yielding insignificant data. There is little to no evidence of empathy, leading to a superficial or incorrect understanding of user needs.
Points
/ 30 pts

Clarity and Relevance of Jobs To Be Done Framework:
view longer description
30 pts
Excellent
The student clearly identifies and articulates both functional and emotional jobs with well-defined desired outcomes and metrics of success. The problem statements are data-driven, aligning closely with stakeholder needs, and effectively transform problems into opportunities for innovation.
24 pts
Very Good
The student identifies most functional and emotional jobs with relevant desired outcomes. The problem statements are generally data-driven but may lack some detail in aligning with stakeholder needs or framing opportunities for innovation.
18 pts
Satisfactory
The student identifies some functional and emotional jobs but with limited detail or relevance. The problem statements are somewhat data-driven but may be generic or not fully aligned with stakeholder needs.
12 pts
Fair
The student struggles to identify functional and emotional jobs, with vague or poorly articulated outcomes. The problem statements are weakly supported by data, failing to effectively frame opportunities for innovation.
6 pts
Poor
The student fails to identify relevant jobs or outcomes, and the problem statements are disconnected from data and stakeholder needs, showing little understanding of how to frame opportunities.
Points
/ 30 pts

Depth of Persona Development:
view longer description
30 pts
Excellent
The personas are thoroughly developed with detailed insights into what the users think, see, feel, and do. The student provides comprehensive and nuanced descriptions that effectively inform design decisions and demonstrate a deep understanding of user behaviors and motivations.
24 pts
Very Good
The personas are well-developed with clear insights into user behaviors and motivations. Most aspects of think, see, feel, and do are covered, though some areas could be more detailed or better integrated into design decisions.
18 pts
Satisfactory
The personas are adequately developed with basic insights into user behaviors and motivations. Some aspects may be underdeveloped or lack integration with design decisions.
12 pts
Fair
The personas are poorly developed, with superficial or incomplete insights into user behaviors and motivations. There is limited application of these insights to inform design decisions.
6 pts
Poor
The personas are very underdeveloped, with little to no insight into what users think, see, feel, and do. There is no clear connection between the personas and the design decisions.
Points
/ 30 pts

Total Points: 0 out of 100"""

       ),




 

        
       "W5- Individual Assignment- 'What Is?' Stage": (       
       """
Criteria	Ratings	Pts
Peer Learning
view longer description
10 pts
Excellent
Commenting and offering feedback to at least 2 peers
6 pts
Satisfactory
Commenting on a peer's answers
0 pts
No Marks
No comments or feedback offered to peers.
Points
/ 10 pts

Time Management
view longer description
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
Points
/ 10 pts

Criteria 1: Identification of Challenges in Project Selection
view longer description
25 pts
Excellent
Clearly identifies multiple challenges in project selection with detailed and specific examples, demonstrating a strong ability to discern when and how to appropriately apply Design Thinking principles to various contexts.
20 pts
Very Good
Identifies several challenges with relevant examples, showing good discernment in applying Design Thinking principles to project selection.
15 pts
Satisfactory
Identifies some challenges with basic examples, demonstrating a general ability to discern the application of Design Thinking principles.
10 pts
Fair
Identifies few challenges with minimal examples, showing limited discernment in applying Design Thinking principles.
5 pts
Poor
Identifies very few or no challenges with no examples, demonstrating minimal to no discernment in the application of Design Thinking principles.
Points
/ 25 pts

Criteria 2: Understanding Integration of Design Thinking with Engineering Thinking
view longer description
30 pts
Excellent
Provides a thorough explanation of the integration challenges, including specific examples and contexts. Demonstrates strong familiarity with Design Thinking frameworks and effectively relates them to engineering thinking processes.
24 pts
Very Good
Offers a good explanation of integration challenges with relevant examples. Shows good familiarity with Design Thinking frameworks and relates them well to engineering thinking processes.
18 pts
Satisfactory
Provides a basic explanation of integration challenges with some examples. Shows general familiarity with Design Thinking frameworks and relates them to engineering thinking processes.
12 pts
Fair
Offers a limited explanation of integration challenges with few examples. Shows limited familiarity with Design Thinking frameworks and a minimal relation to engineering thinking processes.
6 pts
Poor
Provides a minimal explanation of integration challenges with no examples. Shows little to no familiarity with Design Thinking frameworks and does not relate them to engineering thinking processes.
Points
/ 30 pts

Criteria 3: Strategies for Overcoming Challenges
view longer description
25 pts
Excellent
Proposes detailed and effective strategies for overcoming challenges, including insightful strategic guidance that aligns with project goals and stakeholder needs. Demonstrates a high level of strategic thinking and leadership.
20 pts
Very Good
Suggests practical strategies for overcoming challenges with relevant strategic guidance. Shows good strategic thinking and alignment with project goals and stakeholder needs.
15 pts
Satisfactory
Provides basic strategies for overcoming challenges with some strategic guidance. Demonstrates general strategic thinking and alignment with project goals and stakeholder needs.
10 pts
Fair
Offers limited strategies for overcoming challenges with minimal strategic guidance. Shows limited strategic thinking and alignment with project goals and stakeholder needs.
5 pts
Poor
Proposes minimal strategies for overcoming challenges with no strategic guidance. Demonstrates little to no strategic thinking and alignment with project goals and stakeholder needs.
Points
/ 25 pts

Total Points: 0 out of 100
"""
 
        ),
       
       
       
       
       
           
        "W5- Project Assignment- Insights & Design Criteria": (
       """
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome

Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Clarity and Relevance of Insights:
This is related to the left side of the table the Insights
Learning Outcome 1.2.c Insight-Driven Problem Framing
40 pts
Excellent
The insights are exceptionally clear, demonstrating a deep understanding of the problem and effectively framing it in a way that drives design decisions. The connection between research findings and insights is well-articulated, showing strong evidence of insightful problem framing.
32 pts
Very Good
The insights are clear and relevant, showing a solid understanding of the problem. The framing of the problem is well-executed with only minor gaps in connecting the research findings to the insights.
24 pts
Satisfactory
The insights are generally clear, but may lack depth or full relevance to the problem framing. The connection between research findings and insights is present but somewhat weak or underdeveloped.
16 pts
Fair
Insights are unclear or lack relevance, with significant gaps in problem framing. The connection between research findings and insights is poorly articulated or missing key elements.
8 pts
Poor
Insights are vague, irrelevant, or incorrect. There is little to no connection between research findings and the insights presented, indicating a lack of understanding and poor problem framing.
40 pts

This criterion is linked to a Learning Outcome
Rationale for Design Criteria Selection:
This is related to the right side of the table the Design Criteria and how it's connected to the left side.
Learning Outcome 5.2.b Strategic Guidance
50 pts
Excellent
The design criteria are thoroughly justified with a clear and logical rationale that reflects strategic thinking. The criteria are well-aligned with user needs, business goals, and technical constraints, showing the ability to provide strategic guidance in design decisions.
40 pts
Very Good
The design criteria are well-justified, with a clear rationale connecting the insights to the chosen criteria, demonstrating strategic thought. Minor areas may need stronger connections, but overall, the alignment is solid and strategically sound.
30 pts
Satisfactory
The design criteria are justified, though the rationale may lack depth or clarity. The connection between insights and criteria is present but may be weak, with strategic considerations somewhat underdeveloped.
20 pts
Fair
The design criteria are poorly justified, with a weak or unclear rationale. The connection to the insights is tenuous, leading to misalignment with strategic goals and user needs.
10 pts
Poor
The design criteria lack justification, with little to no rationale provided. The connection between the insights and the design criteria is absent or fundamentally flawed, showing a lack of strategic guidance.
50 pts
Total Points: 100
"""

        ),

        
        

         "W7- Project Assignment- Brainstorming- Convergence": (           
          """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome

Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Understanding of Convergence:
This is related to Q1
Learning Outcome 
4.1.c - Session Design for Convergence and Divergence:
25 pts
Excellent
The student thoroughly articulates the converging phase, explaining its role in narrowing down ideas to a feasible solution by systematically reducing options based on predefined criteria. A clear distinction is made between the converging and diverging phases, demonstrating an advanced understanding of the purpose and process of each stage.
20 pts
Very Good
The student explains the converging phase well, showing an understanding of how ideas are refined and selected. Some minor details on the comparison with the diverging phase may be lacking, but overall, the explanation is well-structured.
15 pts
Satisfactory
The student provides a basic explanation of the converging phase, with limited detail on how it differs from the diverging phase. The description might be overly simplified or lack depth but demonstrates general awareness.
10 pts
Fair
The student demonstrates only a vague understanding of the converging phase, failing to clearly distinguish it from the diverging phase. The explanation may be confused or incomplete.
5 pts
Poor
The student does not adequately explain the converging phase, showing little to no understanding of its role or how it contrasts with the diverging phase.
25 pts

This criterion is linked to a Learning Outcome
Converging Tools and Techniques:
This is related to Q2
Learning Outcome 
2.1.c - Prioritise Ideas:
45 pts
Excellent
The student identifies and applies multiple specific tools effectively to converge ideas, providing a clear rationale for how each tool helps narrow down options. The answer demonstrates an advanced ability to critically evaluate the relevance of each technique in refining ideas for the project.
36 pts
Very Good
The student discusses two or more tools and techniques for converging ideas, explaining how they helped in narrowing down ideas. Some tools may lack detailed justification, but the overall rationale for their selection is solid.
27 pts
Satisfactory
The student identifies at least one tool or technique used to converge ideas but provides limited detail on how it was applied or how it helped refine the brainstormed ideas. The explanation is adequate but lacks depth.
18 pts
Fair
The student mentions tools or techniques for convergence but fails to explain how they were applied in the context of the project. The rationale for selecting these tools is weak or unclear.
9 pts
Poor
The student either fails to identify relevant tools for convergence or provides an inadequate explanation of their application and effectiveness.
45 pts

This criterion is linked to a Learning Outcome
Alignment with Project Goals:
This is related to Q3
Learning Outcome 
5.2.b Strategic Guidance:
20 pts
Excellent
The decision-making criteria are clearly articulated and demonstrate a strong alignment with both the overarching project goals and the specific user needs. Each criterion directly supports achieving project success, reflecting a deep understanding of how the selected ideas address key project objectives and user challenges.
16 pts
Very Good
The criteria reflect a solid understanding of the project goals, with most of the selected ideas aligning well with the intended outcomes. Minor gaps exist in fully connecting all ideas to the user needs or project objectives, but the overall alignment remains robust.
12 pts
Satisfactory
The student identifies at least one tool or technique used to converge ideas but provides limited detail on how it was applied or how it helped refine the brainstormed ideas. The explanation is adequate but lacks depth.
8 pts
Fair
The student mentions tools or techniques for convergence but fails to explain how they were applied in the context of the project. The rationale for selecting these tools is weak or unclear.
4 pts
Poor
The decision-making criteria are either absent or fail to address the project goals and user needs. The ideas selected show no strategic alignment, undermining the overall effectiveness of the converging phase.
20 pts
Total Points: 100
"""
       ),      
        
        
        
        
        "W6- Individual Assignment- Brainstorming (Divergent)": (       
        """
Criteria	Ratings	Pts
Time Management
view longer description
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
Points
/ 10 pts

Understanding of Divergence and Convergence
view longer description
25 pts
Excellent
Clearly explains the purpose of both divergent and convergent phases. Demonstrates an insightful understanding of how divergence encourages broad exploration of ideas, while convergence focuses on refining and selecting the best solutions.
20 pts
Very Good
Explains both phases with a good level of understanding, with some reflection on the benefits of each phase in the design thinking process.
15 pts
Satisfactory
Provides a basic distinction between divergence and convergence but lacks depth in explaining their significance.
10 pts
Fair
Shows limited understanding of one or both phases, with little reflection on their importance in brainstorming.
5 pts
Poor
Does not demonstrate an understanding of the differences between the two phases or confuses the concepts entirely.
Points
/ 25 pts

Selection, Justification, and Reflection on Brainstorming Methods
view longer description
30 pts
Excellent
Clearly identifies the brainstorming method(s) used, providing a strong justification based on the project's needs. Demonstrates deep insight into how the method(s) fostered creativity and diverse idea generation. Reflects thoroughly on what was learned from the application, showing a clear connection between the method’s outcomes and the project’s progress or results.
24 pts
Very Good
Identifies and justifies the brainstorming method(s) well, explaining how the method supported divergent thinking. Provides a good reflection on the learning outcomes, linking them to specific project elements, though with slightly less depth.
18 pts
Satisfactory
Describes the brainstorming method(s) used with some justification, but lacks a detailed explanation of why the method(s) were chosen. Reflection on what was learned is present but lacks depth or clear connection to the project's outcomes.
12 pts
Fair
Mentions a brainstorming method but offers limited justification and weak insight into its relevance to the project. Reflection on learning is minimal and lacks clear links to the project.
6 pts
Poor
Fails to appropriately identify or justify the brainstorming method(s) used. No meaningful reflection on what was learned, or how the method impacted the project.
Points
/ 30 pts

Selection, Justification, and Reflection on Brainstorming Methods
view longer description
35 pts
Excellent
Provides a clear and detailed description of specific challenges encountered during brainstorming, demonstrating an insightful understanding of group dynamics, technical constraints, or cognitive barriers. Offers well-considered and effective strategies to address these challenges, showing a deep understanding of facilitation techniques, collaborative problem-solving, and adaptability in group settings.
28 pts
Very Good
Identifies relevant challenges with good detail and understanding. Provides practical and mostly effective strategies for overcoming these challenges, with some reflection on their impact and success in facilitating the brainstorming session.
21 pts
Satisfactory
Describes general challenges with some basic solutions, but lacks depth or specificity in both the challenges identified and the methods used to resolve them. Reflection on the success of the strategies may be limited.
14 pts
Fair
Mentions challenges in a superficial manner, offering limited or vague strategies that are not thoroughly explained or aligned with the challenges described.
7 pts
Poor
Fails to identify any meaningful challenges or does not propose any viable strategies for addressing them. Solutions, if provided, are irrelevant or ineffective in the context of the challenges faced.
Points
/ 35 pts

Total Points: 0 out of 100
"""
      ),





         "W7- Project Assignment- Brainstorming- Convergence": (           
          """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome

Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Understanding of Convergence:
This is related to Q1
Learning Outcome 
4.1.c - Session Design for Convergence and Divergence:
25 pts
Excellent
The student thoroughly articulates the converging phase, explaining its role in narrowing down ideas to a feasible solution by systematically reducing options based on predefined criteria. A clear distinction is made between the converging and diverging phases, demonstrating an advanced understanding of the purpose and process of each stage.
20 pts
Very Good
The student explains the converging phase well, showing an understanding of how ideas are refined and selected. Some minor details on the comparison with the diverging phase may be lacking, but overall, the explanation is well-structured.
15 pts
Satisfactory
The student provides a basic explanation of the converging phase, with limited detail on how it differs from the diverging phase. The description might be overly simplified or lack depth but demonstrates general awareness.
10 pts
Fair
The student demonstrates only a vague understanding of the converging phase, failing to clearly distinguish it from the diverging phase. The explanation may be confused or incomplete.
5 pts
Poor
The student does not adequately explain the converging phase, showing little to no understanding of its role or how it contrasts with the diverging phase.
25 pts

This criterion is linked to a Learning Outcome
Converging Tools and Techniques:
This is related to Q2
Learning Outcome 
2.1.c - Prioritise Ideas:
45 pts
Excellent
The student identifies and applies multiple specific tools effectively to converge ideas, providing a clear rationale for how each tool helps narrow down options. The answer demonstrates an advanced ability to critically evaluate the relevance of each technique in refining ideas for the project.
36 pts
Very Good
The student discusses two or more tools and techniques for converging ideas, explaining how they helped in narrowing down ideas. Some tools may lack detailed justification, but the overall rationale for their selection is solid.
27 pts
Satisfactory
The student identifies at least one tool or technique used to converge ideas but provides limited detail on how it was applied or how it helped refine the brainstormed ideas. The explanation is adequate but lacks depth.
18 pts
Fair
The student mentions tools or techniques for convergence but fails to explain how they were applied in the context of the project. The rationale for selecting these tools is weak or unclear.
9 pts
Poor
The student either fails to identify relevant tools for convergence or provides an inadequate explanation of their application and effectiveness.
45 pts

This criterion is linked to a Learning Outcome
Alignment with Project Goals:
This is related to Q3
Learning Outcome 
5.2.b Strategic Guidance:
20 pts
Excellent
The decision-making criteria are clearly articulated and demonstrate a strong alignment with both the overarching project goals and the specific user needs. Each criterion directly supports achieving project success, reflecting a deep understanding of how the selected ideas address key project objectives and user challenges.
16 pts
Very Good
The criteria reflect a solid understanding of the project goals, with most of the selected ideas aligning well with the intended outcomes. Minor gaps exist in fully connecting all ideas to the user needs or project objectives, but the overall alignment remains robust.
12 pts
Satisfactory
The student identifies at least one tool or technique used to converge ideas but provides limited detail on how it was applied or how it helped refine the brainstormed ideas. The explanation is adequate but lacks depth.
8 pts
Fair
The student mentions tools or techniques for convergence but fails to explain how they were applied in the context of the project. The rationale for selecting these tools is weak or unclear.
4 pts
Poor
The decision-making criteria are either absent or fail to address the project goals and user needs. The ideas selected show no strategic alignment, undermining the overall effectiveness of the converging phase.
20 pts
Total Points: 100
"""
       ),      
        
        
        
        
        
        
        "W7- Individual Assignment- Alignment & Emergence": (         
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Understanding of Alignment:
This is related to Q1
35 pts
Excellent
Demonstrates a thorough understanding of alignment by clearly defining how aligning the problem statement with user needs, business objectives, and technical constraints ensures the project is solving the right problem. Explains the value of alignment in preventing project misdirection and enhancing the relevance of design solutions.
28 pts
Very Good
Adequately explains alignment and provides some insight into its importance in ensuring the problem is correctly framed. Mentions the benefits of alignment but lacks depth in connecting to all critical factors like user needs or business goals.
21 pts
Satisfactory
Defines alignment but with limited insight into how it practically impacts the design process. Provides a basic explanation but fails to fully address the implications of misalignment in a project.
14 pts
Fair
Provides a vague or incomplete definition of alignment, offering minimal understanding of its significance. Lacks concrete examples or connection to project success.
7 pts
Poor
Fails to define alignment effectively. Provides no understanding of its value or how misalignment could affect a design project.
35 pts

This criterion is linked to a Learning Outcome
Understanding of Emergence:
This is related to Q2
35 pts
Excellent
Provides a detailed and insightful explanation of emergence as the spontaneous development of ideas or solutions during the iterative design process. Clearly illustrates with a specific example from their project where initial ideas evolved or new insights emerged from collaborative ideation.
28 pts
Very Good
Offers a solid explanation of emergence with some connection to how ideas evolve naturally during group discussions or prototyping. The example given is relevant but may lack detail on how it shaped the final design.
21 pts
Satisfactory
Provides a basic description of emergence but lacks depth or clear linkage to its impact on idea evolution. The project example is present but may not fully explain how emergence influenced the design process.
14 pts
Fair
Offers a vague explanation of emergence, with limited or incomplete references to the iterative nature of design. The example from the project may not directly demonstrate how emergence occurred.
7 pts
Poor
Fails to define emergence accurately and provides little to no relevant example from the project, demonstrating limited understanding of the concept.
35 pts

This criterion is linked to a Learning Outcome
Takeaways or Aha Moments:
This is related to Q3
20 pts
Excellent
Articulates deep insight into the interplay between alignment and emergence, recognizing that both are necessary for balancing structure and flexibility in the design process. Clearly reflects on specific lessons learned, such as the importance of revisiting alignment and how emergence can lead to innovation when ambiguity is embraced.
16 pts
Very Good
Provides a thoughtful analysis of the lessons learned regarding alignment and emergence. The response captures their importance but may not fully articulate the dynamic interaction between the two.
12 pts
Satisfactory
Offers a general reflection on alignment and emergence but lacks depth in linking the two concepts. Lessons learned are mentioned but remain somewhat superficial or generic.
8 pts
Fair
Presents a limited or disjointed understanding of the role of alignment and emergence in design projects. Lessons learned may be incomplete or not clearly connected to practical project experiences.
4 pts
Poor
Fails to present a clear understanding of the relationship between alignment and emergence. Provides no substantial reflection on lessons learned.
20 pts
Total Points: 100
"""
 
         ),
        


         

        "W8- Project Assignment- Key Assumptions": ( 
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline.
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Clarity and Depth of Key Assumptions:
1.2.c - Insight-Driven Problem Framing: Promoting evidence-based decision-making by using insights to shape problem framing.
50 pts
Excellent
The key assumptions are clearly articulated, demonstrating a deep understanding of the project. Each assumption is backed by comprehensive insights and relevant data, effectively supporting the project's problem framing.
40 pts
Very Good
Key assumptions are clearly stated, and most are supported with relevant insights. However, one or two assumptions may lack depth or full integration into the overall problem frame.
30 pts
Satisfactory
Assumptions are identified, but there is limited reflection or lack of depth. Some assumptions may be vague or lack clear evidence or connection to the project.
20 pts
Fair
Assumptions are unclear or inconsistently defined. Little effort is made to link assumptions to project insights or data.
10 pts
Poor
The submission lacks clarity in articulating assumptions or fails to show any substantial reflection on project insights
50 pts

This criterion is linked to a Learning Outcome
Identification of Biases and Assumptions:
2.3.b - Build Iteratively with Assumption Testing: Testing assumptions through user feedback.
40 pts
Excellent
The submission effectively identifies potential biases in the assumptions and discusses methods to test and mitigate them. There is a clear understanding of how these assumptions could impact the project outcome.
32 pts
Very Good
Biases in the assumptions are identified, but there is limited discussion on how they would be tested or mitigated.
24 pts
Satisfactory
Some biases are mentioned, but there is little depth in understanding their impact or how they would be addressed in the project.
16 pts
Fair
Few biases are identified, and no clear plan for addressing or testing them is presented.
8 pts
Poor
No effort is made to identify or discuss biases in the assumptions.
40 pts
Total Points: 100
"""
         ),
        
         
        
        
        
        
        "W8- Individual Assignment- Assumption Testing": (                         
        """
Criteria	Ratings	Pts
This criterion is linked to a Learning Outcome
Time Management:
This is based on the assignment submission date.
10 pts
Before Deadline
Assignment Submitted before the deadline.
8 pts
Around the Deadline
Assignment Submitted max 2 days after the deadline.
6 pts
About a week late
Assignment Submitted 3-7 days after the deadline
4 pts
More than 1 week late
Assignment Submitted 8-14 days after the deadline.
2 pts
Later than 2 weeks
Assignment Submitted more than 2 weeks after the deadline.
10 pts

This criterion is linked to a Learning Outcome
Understanding and Application of Assumption Surfacing Techniques:
Related to Learning Outcome 
1.1.c Awareness of Bias and Assumptions:
40 pts
Excellent
Demonstrates a comprehensive understanding of multiple techniques for surfacing assumptions; examples provided are specific, insightful, and well-integrated with software engineering practices.
32 pts
Very Good
Demonstrates a good understanding of various techniques; examples provided are relevant but may lack depth or integration with specific software engineering contexts.
24 pts
Satisfactory
Shows basic understanding with generic examples; techniques mentioned are correct but superficially explored.
16 pts
Fair
Limited understanding; examples are minimal or partially incorrect.
8 pts
Poor
Displays little to no understanding of the techniques; examples are irrelevant or missing.
40 pts

This criterion is linked to a Learning Outcome
Effectiveness in Challenging and Testing Assumptions:
Related to to Learning Outcome
2.3.b Build Iteratively with Assumption Testing:
30 pts
Excellent
Provides a detailed and methodical approach for challenging and testing assumptions, with a strong emphasis on iterative development and integration of user feedback.
24 pts
Very Good
Describes a clear approach with some detail; user feedback is considered but could be more deeply integrated into the process.
18 pts
Satisfactory
Basic description of the process; user feedback is mentioned but not effectively linked to the testing of assumptions.
12 pts
Fair
The approach is vague or only partially relevant; there is minimal mention of user feedback.
6 pts
Poor
Lacks understanding of the process; fails to mention or incorrectly describes the role of user feedback.
30 pts

This criterion is linked to a Learning Outcome
Application of Past Learnings to Enhance Current Project Strategies:
Related to Learning Outcome 
5.2.b Strategic Guidance
20 pts
Excellent
Demonstrates a profound ability to extract and apply lessons learned from past experiences to significantly enhance the strategic direction of current projects. Clearly articulates how specific past learnings led to improved decision-making and project outcomes.
16 pts
Very Good
Effectively identifies valuable lessons from past projects and explains how they have informed current strategic choices, showing clear links between past experiences and current practices.
12 pts
Satisfactory
Identifies general learnings from previous experiences and makes basic connections to current project strategies, but the impact on strategic decision-making is not thoroughly articulated.
8 pts
Fair
Makes limited connections between past experiences and current strategies; reflections on past learnings are somewhat relevant but lack depth and impact on current decision-making.
4 pts
Poor
Shows little to no understanding of how past experiences can inform current project strategies; fails to make relevant connections or reflect on past learnings.
20 pts
Total Points: 100
""" 
       ),     
      
        
          # Tech MBA RUBRICS



         "M1 W1 Assignment: Analysing the Drivers behind Digital Transformation": ( 
"""
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Analysis of Digital Transformation Drivers:
5 pts
Excellent
Thoroughly discusses at least three key drivers with exceptional clarity and insight. Demonstrates an exceptional understanding of how these drivers are influencing digital transformation in the chosen subject. Provides insightful examples and evidence to support the analysis.
4 pts
Very Good
Discusses at least three key drivers in a clear and concise manner. Shows a strong understanding of how these drivers influence digital transformation. Provides relevant examples and evidence to support the analysis.
3 pts
Satisfactory
Discusses three key drivers but may lack some depth in analysis. Demonstrates a satisfactory understanding of how these drivers influence digital transformation. Provides some examples and evidence.
2 pts
Fair
Discusses fewer than three key drivers, and the analysis is limited. Shows a basic understanding of digital transformation drivers but lacks depth. Provides minimal examples or evidence.
1 pts
Poor
Fails to discuss digital transformation drivers effectively or provides inaccurate information. Demonstrates a lack of understanding of the key drivers. Lacks examples and evidence.
5 pts

This criterion is linked to a Learning Outcome
Analysis of Impact:
5 pts
Excellent
Provides a comprehensive and insightful analysis of the impact of digital transformation on the industry or organization. Clearly identifies and explains how it has transformed operations, customer experiences, and business models. Supported by compelling examples and evidence.
4 pts
Very Good
Offers a clear analysis of the impact of digital transformation. Identifies and explains how it has transformed operations, customer experiences, and business models. Provides relevant examples and evidence.
3 pts
Satisfactory
Presents a reasonable analysis of the impact of digital transformation. Discusses changes in operations, customer experiences, and business models, but may lack some depth. Offers some examples and evidence.
2 pts
Fair
Provides limited analysis of the impact of digital transformation. Discusses changes superficially and with minimal depth. Offers few examples or evidence.
1 pts
Poor
Fails to analyze the impact of digital transformation effectively or provides inaccurate information. Demonstrates a lack of understanding of the impact. Lacks examples and evidence.
5 pts

This criterion is linked to a Learning Outcome
Reflection on Learning:
5 pts
Excellent
Offers a thoughtful and insightful reflection on the assignment, demonstrating a deep understanding of the subject matter. Clearly articulates how the learning from this analysis can be applied to their role or industry with innovative and well-supported ideas.
4 pts
Very Good
Provides a clear reflection on the assignment, indicating a good understanding of the subject matter. Articulates how the learning can be applied to their role or industry with relevant ideas and examples.
3 pts
Satisfactory
Offers a basic reflection on the assignment, demonstrating a reasonable understanding of the subject matter. Indicates how the learning can be applied to their role or industry with some relevant ideas.
2 pts
Fair
Provides a limited reflection with minimal depth. Offers basic ideas about the application of learning to their role or industry but lacks detail or relevance.
1 pts
Poor
Fails to provide a meaningful reflection or application of learning. Demonstrates a lack of understanding or relevance in applying the knowledge.
5 pts

This criterion is linked to a Learning Outcome
Demonstrate a deep understanding of the drivers behind digital transformation to formulate well-structured strategies
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--
This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--
Total Points: 15
"""
             
             
         ),


         "Module 4 Project: Strategic Responsible AI plan": ( 
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Data Privacy Considerations:
5 pts
Excellent
Provides a comprehensive discussion on data privacy considerations, clear identification of sensitive data, thorough proposed measures, and detailed outline of storage methods.
4 pts
Very Good
Offers a thorough discussion on data privacy considerations with clear identification of sensitive data and proposed measures.
3 pts
Satisfactory
Adequately discusses data privacy considerations with some identification of sensitive data and proposed measures.
2 pts
Fair
Provides a basic discussion on data privacy considerations with limited identification of sensitive data and proposed measures.
1 pts
Poor
Fails to adequately discuss data privacy considerations or identify sensitive data and proposed measures.
5 pts

This criterion is linked to a Learning Outcome
Identification of Bias Scenarios:
5 pts
Excellent
Clearly identifies two potential bias scenarios with detailed explanations and strong links to the Primeflix Gen-AI solution.
4 pts
Very Good
Identifies two bias scenarios with detailed explanations and relevant links to the Primeflix Gen-AI solution.
3 pts
Satisfactory
Identifies two bias scenarios with adequate explanations and some links to the Primeflix Gen-AI solution.
2 pts
Fair
Identifies one bias scenario with limited explanations and weak links to the Primeflix Gen-AI solution.
1 pts
Poor
Fails to adequately identify bias scenarios or provide relevant explanations.
5 pts

This criterion is linked to a Learning Outcome
Best Practices for Employee Understanding:
5 pts
Excellent
Provides a clear example of best practices for aiding employee understanding with effective use of open-source tools and thorough explanations.
4 pts
Very Good
Offers a clear example of best practices for aiding employee understanding with effective use of open-source tools and detailed explanations.
3 pts
Satisfactory
Presents an example of best practices with adequate use of open-source tools and explanations.
2 pts
Fair
Presents a basic example of best practices with limited use of open-source tools and explanations.
1 pts
Poor
Fails to adequately provide an example of best practices or use open-source tools effectively.
5 pts

This criterion is linked to a Learning Outcome
Implementation of AI Governance Mechanisms:
5 pts
Excellent
Identifies two main best practices with clear contextualization to the Primeflix Gen-AI solution and strong links to ethical/privacy and/or XAI considerations.
4 pts
Very Good
Identifies two main best practices with clear contextualization to the Primeflix Gen-AI solution and relevant links to ethical/privacy and/or XAI considerations.
3 pts
Satisfactory
Identifies two main best practices with some contextualization to the Primeflix Gen-AI solution and links to ethical/privacy and/or XAI considerations.
2 pts
Fair
Identifies one best practice with limited contextualization to the Primeflix Gen-AI solution and weak links to ethical/privacy and/or XAI considerations.
1 pts
Poor
Fails to adequately identify best practices or provide relevant contextualization and links.
5 pts

This criterion is linked to a Learning Outcome
Formulate AI business strategies that leverage machine, deep learning, and generative AI capabilities to address specific business challenges.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--
 This criterion is linked to a Learning OutcomeTime Management
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--
Total Points: 20
"""
             
             
         ),


         "M1 W3 Assignment: Building Blocks for Organizational Digital Transformation": ( 
"""
Criteria	Ratings	Pts

 This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--
 This criterion is linked to a Learning OutcomeEffectively assess the role of technology as a disruptor and enabler of change within various business contexts
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Detailed Analysis of Chosen Dimensions:
5 pts
Excellent
Provides a thorough and detailed analysis of the selected dimensions. Effectively integrates the selected dimensions into the specific organizational context, providing a clear explanation of how these dimensions align with the company's current state, future goals, and overall strategy.
4 pts
Very Good
Offers a detailed analysis of the selected dimensions. Integrates the selected dimensions into the organizational context, demonstrating an understanding of their relevance to the company's current and future needs.
3 pts
Satisfactory
Meets basic requirements. Provides an analysis of the selected dimensions, offers an explanation of how the selected dimensions align with the organizational context, but there may be areas for improvement in clarity or depth.
2 pts
Fair
Partially meets requirements. Analysis of selected dimensions and integration of selected dimensions into the organizational context may lack clarity or thorough exploration.
1 pts
Poor
Fails to meet the basic requirements. Analysis of selected dimensions and integration of selected dimensions into the organizational context lacks coherence or depth.
5 pts

This criterion is linked to a Learning Outcome
Strategic Insight and Recommendations:
5 pts
Excellent
Demonstrates strategic insight by offering well-founded recommendations on how the organization should handle or leverage the identified dimensions to navigate technological disruption and capitalize on opportunities.
4 pts
Very Good
Provides sound strategic recommendations based on a comprehensive understanding of the identified dimensions and their impact on technological disruption and business enablement.
3 pts
Satisfactory
Meets basic requirements. Offers reasonable strategic recommendations, but there may be areas for improvement in depth or specificity.
2 pts
Fair
Partially meets requirements. Strategic recommendations may lack depth or may not fully leverage the potential of the identified dimensions.
1 pts
Poor
Fails to meet the basic requirements. Strategic recommendations lack clarity, depth, and fail to demonstrate a clear understanding of how to leverage the identified dimensions for organizational benefit.
5 pts

Total Points: 10
"""
             
             
         ),
         
         
          "M2 W1 Assignment: Benchmarking Data Leadership Against Industry Leaders": ( 
"""
Criteria    Ratings    Pts

 This criterion is linked to a Learning Outcome
Assess the significance of data leadership in contemporary organisations:
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Company Analysis:
5 pts
Excellent
The analysis provides a thorough and insightful summary of the chosen data-driven company (Amazon, Netflix, Starbucks). It clearly identifies and explains key aspects of their data practices contributing to success.
4 pts
Very Good
The analysis is comprehensive, covering essential elements of the chosen company's data practices. It effectively highlights the key factors contributing to the organization's success.
3 pts
Satisfactory
The analysis provides a basic summary of the chosen company's data practices. It mentions some relevant points but lacks depth and may miss crucial aspects.
2 pts
Fair
The analysis is limited and lacks detail. It only briefly touches on the chosen company's data practices without offering substantial insights.
1 pts
Poor
The analysis is vague and lacks clarity. It fails to provide a meaningful understanding of the chosen company's data practices.
5 pts

This criterion is linked to a Learning Outcome
Gap Analysis:
5 pts
Excellent
The gap analysis thoroughly compares the chosen organization's data practices with those of the industry leader. It identifies and analyzes significant gaps with precision and depth.
4 pts
Very Good
The gap analysis is comprehensive, highlighting key differences between the chosen organization and the industry leader. It offers a solid understanding of existing gaps.
3 pts
Satisfactory
The gap analysis identifies some differences between the chosen organization and the industry leader but lacks depth or may miss certain crucial aspects.
2 pts
Fair
The gap analysis is limited and provides only a superficial comparison. It lacks detailed insights into the differences between the two organizations.
1 pts
Poor
The gap analysis is unclear or nonexistent. It fails to effectively compare the chosen organization with the industry leader in terms of data practices.
5 pts

This criterion is linked to a Learning Outcome
Actionable Insights:
5 pts
Excellent
The proposed recommendations are highly specific, practical, and directly address the identified gaps. They demonstrate a deep understanding of data leadership standards and offer innovative solutions.
4 pts
Very Good
The recommendations are clear, relevant, and aligned with the identified gaps. They provide practical suggestions for the organization to enhance its data practices.
3 pts
Satisfactory
The recommendations are reasonable but may lack specificity or originality. They offer general guidance on improving data practices without detailed implementation strategies.
2 pts
Fair
The recommendations are vague or generic, providing limited guidance for the organization to improve its data practices. They lack depth or innovative insights.
1 pts
Poor
The recommendations are unclear or irrelevant. They fail to address the identified gaps or provide meaningful guidance for the organization to improve its data practices.
5 pts

 This criterion is linked to a Learning Outcome
 Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 15
"""
             
             
         ),        



         "Module 6: Self-Reflective Assignment": ( 
"""
Criteria	Ratings	Pts
 This criterion is linked to a Learning Outcome
 Assess the strategic value of the selected technology within a business context:
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Assess the strategic value of the selected technology within a business context:
5 pts
Excellent
The student provides a comprehensive and insightful analysis of the strategic value of the selected technology within the business context. They demonstrate a deep understanding of how the technology aligns with the organization's goals and objectives, identifying clear opportunities for leveraging the technology to drive competitive advantage.
4 pts
Very Good
The student offers a detailed analysis of the strategic value of the selected technology, highlighting key aspects of its relevance to the business context. They effectively articulate the potential benefits and implications of technology integration, although some areas may lack depth or clarity.
3 pts
Satisfactory
The student provides a basic assessment of the strategic value of the selected technology, identifying some relevant points but lacking in-depth analysis or insight. The evaluation may lack specificity or fail to address key aspects of technology alignment with business strategy.
2 pts
Fair
The student's assessment of the strategic value of the selected technology is limited in scope and lacks depth. They may offer superficial insights or fail to connect the technology's potential impact to broader organizational goals effectively.
1 pts
Poor
The student's assessment of the strategic value of the selected technology is inadequate or nonexistent. They demonstrate a lack of understanding of how the technology relates to the business context and fail to identify meaningful opportunities for its integration.
5 pts

 This criterion is linked to a Learning OutcomeAnalyse the potential impact of technology integration on organisational processes and outcomes:
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Analyze the potential impact of technology integration on organizational processes and outcomes:
5 pts
Excellent
The student conducts a thorough and insightful analysis of the potential impact of technology integration on organizational processes and outcomes. They demonstrate a comprehensive understanding of how the technology will influence various aspects of the organization, including operations, performance, and innovation.
4 pts
Very Good
The student offers a detailed analysis of the potential impact of technology integration, highlighting key processes and outcomes affected by the technology. They provide thoughtful insights into the implications of technology adoption, although some aspects may require further elaboration or clarification.
3 pts
Satisfactory
The student provides a basic analysis of the potential impact of technology integration, identifying some relevant processes and outcomes but lacking depth or specificity. The evaluation may overlook certain aspects of technology influence on organizational dynamics.
2 pts
Fair
The student's analysis of the potential impact of technology integration is limited or superficial. They may offer generic observations without providing meaningful insights into specific processes or outcomes affected by the technology.
1 pts
Poor
The student fails to analyze the potential impact of technology integration on organizational processes and outcomes. Their evaluation lacks substance or relevance, demonstrating a lack of understanding of the technology's implications for the organization.
5 pts

This criterion is linked to a Learning Outcome
Formulate strategies for the effective and sustainable integration of the chosen technology into diverse business domains:
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Formulate strategies for the effective and sustainable integration of the chosen technology into diverse business domains:
5 pts
Excellent
The student develops innovative and well-reasoned strategies for the effective and sustainable integration of the chosen technology into diverse business domains. They demonstrate a sophisticated understanding of the complexities involved in technology adoption and propose actionable recommendations tailored to the organization's needs.
4 pts
Very Good
The student formulates strategic recommendations for technology integration, considering various business domains and addressing key challenges and opportunities. Their strategies show a clear understanding of the requirements for successful implementation, although some aspects may require further elaboration.
3 pts
Satisfactory
The student proposes basic strategies for technology integration, outlining general approaches without delving into specific implementation details or considerations. The recommendations may lack depth or fail to address all relevant aspects of technology adoption.
2 pts
Fair
The student's strategies for technology integration are limited or poorly developed. They may offer simplistic or impractical recommendations that overlook critical factors or fail to align with the organization's goals and objectives.
1 pts
Poor
The student fails to formulate meaningful strategies for technology integration. Their recommendations are vague, impractical, or irrelevant to the organization's needs, demonstrating a lack of understanding of the complexities involved in technology adoption.
5 pts

Total Points: 15
"""
             
             
         ),



         "Module 5 Project: Ethical Governance and Strategic Preparation for AI Singularity": ( 
"""
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Analysis of AI Singularity Impacts:
5 pts
Excellent
Provides a thorough and insightful analysis of the potential impacts of AI singularity in the chosen sector, supported by detailed examples and demonstrating a deep understanding of the complexities involved in AI advancements.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Presents a basic understanding of the impacts with some analysis supported by relevant examples. Shows engagement with the topic.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Provides minimal analysis of the impacts, with little to no support from examples or relevant details. Indicates a lack of engagement with the complexities of AI singularity.
5 pts

This criterion is linked to a Learning Outcome
Development of Practical Ethical Strategies:
5 pts
Excellent
Proposes a comprehensive and innovative strategy that effectively addresses the ethical, societal, and operational challenges identified in the scenario. Demonstrates a nuanced understanding of strategic planning and ethical considerations for AI at singularity levels.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Proposes a clear strategy that addresses many of the challenges. The strategy is well thought out but may lack detail or innovative approaches to more complex issues.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Offers a basic or underdeveloped strategy that fails to effectively address the identified challenges. Shows limited understanding of the complexities of ethical and strategic planning in AI applications.
5 pts

This criterion is linked to a Learning Outcome
Public Relations Strategy Development:
5 pts
Excellent
Develops a robust public relations strategy that effectively communicates AI initiatives, builds public trust, and engages stakeholders through transparent dialogue. Demonstrates deep insight into managing public perceptions and expectations.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Creates an adequate public relations strategy that somewhat addresses the need for transparency and public engagement but lacks innovation or comprehensive stakeholder management.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Provides a minimal or superficial public relations strategy, inadequately addressing the need to manage public perceptions or engage with stakeholders effectively.
5 pts

This criterion is linked to a Learning Outcome
Anticipate future ethical challenges by exploring the concept of singularity and its potential impact on AI integration into business, preparing to address evolving ethical dilemmas:
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

Total Points: 15
"""                        
         ),




         "M5 W3 Assignment: Designing Effective AI Governance Frameworks": ( 
"""
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Interpret AI governance and regulatory frameworks, ensuring that AI-driven business practices comply with legal and ethical standards to minimise risks and promote responsible AI use:
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Analysis of Governance Challenges:
5 pts
Excellent
Provides a comprehensive and insightful analysis of AI governance challenges specific to the chosen industry, supported by detailed examples and demonstrating a deep understanding of the complexities involved in AI regulation and ethics.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Presents a basic understanding of governance challenges with some analysis supported by relevant examples. Shows engagement with the topic and an understanding of common issues in AI governance.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Offers minimal analysis of governance challenges, with little to no support from examples or relevant details. Shows a lack of engagement with the complexities of AI governance.
5 pts

This criterion is linked to a Learning Outcome
Development of AI Governance Framework:
5 pts
Excellent
Proposes a well-structured and innovative AI governance framework that effectively addresses the identified challenges. Demonstrates an advanced understanding of how to implement, monitor, and adapt governance mechanisms over time.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Proposes a basic AI governance framework that addresses some challenges identified. The framework is adequately thought out but lacks depth or a detailed approach to implementation and adaptation.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Provides a minimal or superficial governance framework with little to no effective strategy for addressing the governance challenges identified. Lacks understanding of how to develop a functional and adaptable governance framework.
5 pts

This criterion is linked to a Learning Outcome
Integration of Ethical Principles in Governance Design:
5 pts
Excellent
Excellently integrates ethical principles such as fairness, transparency, accountability, and stakeholder engagement into the governance framework, showing a nuanced and critical approach to ethical AI governance.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Adequately integrates some ethical principles into the governance framework, but the application may lack depth, innovation, or a holistic approach. Shows a commitment to ethical considerations but may not fully capture all necessary aspects.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Shows minimal or incorrect integration of ethical principles in the governance framework, indicating a lack of understanding of the critical role of ethics in AI governance.
5 pts

This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 15
"""
             
             
         ),






         "Module 4: Action Learning Reflection": ( 
"""
Criteria	Ratings	Pts
 This criterion is linked to a Learning Outcome
 Act as an accountable member of your learning and professional community taking ethical and moral responsibilities of your actions as a data scientist and a practitioner researcher in your business context
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
5 pts

 This criterion is linked to a Learning Outcome
 Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
5 pts

This criterion is linked to a Learning Outcome
Depth:
5 pts
Excellent
The learner has written an extensive and clear reflective piece that goes beyond the expected depth.
4 pts
Very Good
The learner has written an extensive and clear reflective piece shows depth and clarity.
3 pts
Satisfactory
The learner has written a clear reflective piece and shows some depth.
2 pts
Fair
The learner has written a reflective piece but lacks clarity and depth.
1 pts
Poor
The learner has failed to write a reflective piece and/or lacks depth and clarity.
5 pts

Total Points: 15
"""
             
             
         ),



         "M4 W1 Asssignment: Business Assignment": ( 
"""
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Clarity of Problem Identification:
All Learning Outcomes
5 pts
Excellent
The business problem or need is clearly identified, demonstrating a deep understanding of the challenges faced by the chosen user type in the context of the travel vlogging platform.
4 pts
Very Good
The business problem or need is well-defined, with minor areas that could be more explicitly articulated.
3 pts
Satisfactory
The business problem or need is identified, but there is room for improvement in clarity and specificity.
2 pts
Fair
The business problem or need is mentioned, but it lacks clarity and may not be entirely relevant to the chosen user type.
1 pts
Poor
The business problem or need is unclear or not identified.
5 pts

This criterion is linked to a Learning Outcome
Innovation and Relevance of Gen-AI Solution:
2 Learning Outcomes:
- Analyse the diverse applications of AI, including Machine Learning, Deep Learning, in various business contexts.
- Evaluate the fundamental principles of (Generative) Artificial Intelligence (GenAI).
5 pts
Excellent
The proposed Gen-AI solution is highly innovative, directly addressing the identified problem, and is relevant to the chosen user type.
4 pts
Very Good
The proposed Gen-AI solution is innovative and relevant but may have some aspects that could be further developed.
3 pts
Satisfactory
The Gen-AI solution is relevant to the problem, but lacks a certain level of innovation or depth.
2 pts
Fair
The Gen-AI solution is mentioned but may not be entirely relevant or innovative for the identified problem.
1 pts
Poor
The proposed Gen-AI solution is not clear or does not effectively address the identified problem.
5 pts


This criterion is linked to a Learning Outcome
Comprehensive Description of Gen-AI Tasks and Architectures:
2 Learning Outcomes:
- Analyse the diverse applications of AI, including Machine Learning, Deep Learning, in various business contexts.
- Evaluate the fundamental principles of (Generative) Artificial Intelligence (GenAI).
5 pts
Excellent
The Gen-AI tasks and architectures involved in the solution are thoroughly described, demonstrating a deep understanding of their application.
4 pts
Very Good
The Gen-AI tasks and architectures are well-described, with minor areas that could be more detailed.
3 pts
Satisfactory
The description of Gen-AI tasks and architectures is adequate, but there is room for improvement in depth and clarity.
2 pts
Fair
The description of Gen-AI tasks and architectures is present but lacks clarity or depth.
1 pts
Poor
The Gen-AI tasks and architectures are not clearly described or may not be relevant to the proposed solution.
5 pts

This criterion is linked to a Learning Outcome
Business Impact/Benefits:
All Learning Outcomes
5 pts
Excellent
The document clearly articulates the anticipated business impact and benefits of the Gen-AI solution for the chosen user type.
4 pts
Very Good
The business impact and benefits are well-explained, with minor areas that could be more explicitly stated.
3 pts
Satisfactory
The document mentions the business impact and benefits, but there is room for improvement in clarity and specificity.
2 pts
Fair
The business impact and benefits are mentioned but lack clarity or may not be entirely relevant to the chosen user type.
1 pts
Poor
The business impact and benefits are not clearly stated or may not align with the proposed Gen-AI solution.
5 pts

This criterion is linked to a Learning Outcome
Analyse the diverse applications of AI, including Machine Learning, Deep Learning, in various business contexts.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Evaluate the fundamental principles of (Generative) Artificial Intelligence (GenAI).
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Formulate AI business strategies that leverage machine, deep learning, and generative AI capabilities to address specific business challenges.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 20
"""
             
             
         ),





         "M4 W3 Assignment: Gen-AI Business Strategy": ( 
"""
Criteria	Ratings	Pts

 This criterion is linked to a Learning Outcome
 Formulate AI business strategies that leverage machine, deep learning, and generative AI capabilities to address specific business challenges.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Problem Identification and Description:
5 pts
Excellent
Clear identification of the problem, thorough description of its implications, and detailed explanation of the proposed LLM solution.
4 pts
Very Good
Clear problem identification, substantial description of implications, and well-supported explanation of the LLM solution.
3 pts
Satisfactory
Adequate problem identification, basic description of implications, and satisfactory explanation of the LLM solution.
2 pts
Fair
Vague problem identification, limited description of implications, and somewhat unclear explanation of the LLM solution.
1 pts
Poor
Unclear problem identification, no or inadequate description of implications, and failure to explain the LLM solution.
5 pts

This criterion is linked to a Learning Outcome
Solution Proposal Clarity and Relevance:
5 pts
Excellent
Clear articulation of the LLM solution, detailed specification of data requirements, mention of relevant tools, and identification of multiple anticipated challenges.
4 pts
Very Good
Clear articulation of the LLM solution, specification of data requirements, mention of tools, and identification of at least one anticipated challenge.
3 pts
Satisfactory
Adequate articulation of the LLM solution, specification of data requirements, mention of tools with limited insights, and identification of at least one anticipated challenge.
2 pts
Fair
Limited articulation of the LLM solution, unclear specification of data requirements, minimal mention of tools, and unclear or superficial identification of an anticipated challenge.
1 pts
Poor
Inadequate articulation of the LLM solution, failure to specify data requirements, no mention of tools, and failure to identify anticipated challenges.
5 pts

This criterion is linked to a Learning Outcome
Business Value and Long-term Impact:
5 pts
Excellent
Clearly outlines business value, describes transformative long-term impact, and demonstrates alignment with Primeflix's goals.
4 pts
Very Good
Presents business value clearly, describes long-term impact, and shows some alignment with Primeflix's goals.
3 pts
Satisfactory
Provides basic outline of business value, mentions long-term impact, and attempts to align with Primeflix's goals.
2 pts
Fair
Offers vague or incomplete outline of business value, mentions long-term impact superficially, and lacks clear alignment with Primeflix's goals.
1 pts
Poor
Fails to outline business value, lacks mention of long-term impact, and shows no alignment with Primeflix's goals.
5 pts

 This criterion is linked to a Learning Outcome
 Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 15
"""
             
             
         ),





         "M5 W1 Assignment: Ethical Principles and Bias in AI: A Hypothetical Case Study Approach": ( 
"""
Criteria	Ratings	Pts

 This criterion is linked to a Learning Outcome
 Evaluate ethical considerations associated with AI implementation in business operations, ensuring alignment with responsible practices and societal values.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Satisfactory
3 pts
Very Good
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Identification and Analysis of Ethical Concerns:
Learning Outcome 1
5 pts
Excellent
Thoroughly identifies and critically analyzes various ethical concerns and biases, demonstrating a deep understanding of their implications.
4 pts
Very Good
Identifies and analyzes most of the significant ethical concerns and biases, showcasing a solid understanding of their implications.
3 pts
Satisfactory
Identifies and analyzes some ethical concerns and biases, although may overlook minor or nuanced issues.
2 pts
Fair
Identifies limited ethical concerns and biases, with minimal depth in analysis.
1 pts
Poor
Fails to identify or adequately analyze ethical concerns and biases within the scenario.
5 pts

This criterion is linked to a Learning Outcome
Application of Ethical Principles:
Learning Outcome 1
5 pts
Excellent
Develops comprehensive strategies rooted in ethical principles, demonstrating a nuanced understanding of their application to combat biases effectively.
4 pts
Very Good
Develops strategies grounded in ethical principles, addressing most identified biases with clarity and effectiveness.
3 pts
Satisfactory
Develops strategies based on ethical principles to address some identified biases, but with some gaps in clarity or effectiveness.
2 pts
Fair
Develops strategies that partially address identified biases but lack coherence or alignment with ethical principles.
1 pts
Poor
Fails to develop strategies or develops ineffective strategies that do not address identified biases or ethical principles adequately.
5 pts

 This criterion is linked to a Learning Outcome
 Interpret AI governance and regulatory frameworks, ensuring that AI-driven business practices comply with legal and ethical standards to minimise risks and promote responsible AI use.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Compliance with Governance and Regulatory Frameworks:
Learning Outcome 2
5 pts
Excellent
Demonstrates a comprehensive understanding of AI governance and regulatory frameworks, accurately applying them to ensure compliance with legal and ethical standards in the scenario.
4 pts
Very Good
Demonstrates a solid understanding of AI governance and regulatory frameworks, applying them effectively to ensure compliance with legal and ethical standards in most aspects of the scenario.
3 pts
Satisfactory
Demonstrates a basic understanding of AI governance and regulatory frameworks, applying them to ensure compliance with some legal and ethical standards in the scenario, with occasional inaccuracies or omissions.
2 pts
Fair
Demonstrates limited understanding of AI governance and regulatory frameworks, with inconsistent or unclear application to ensure compliance with legal and ethical standards in the scenario.
1 pts
Poor
Fails to demonstrate understanding or application of AI governance and regulatory frameworks to ensure compliance with legal and ethical standards in the scenario.
5 pts

This criterion is linked to a Learning Outcome
Promotion of Responsible AI Use:
Learning Outcome 2
5 pts
Excellent
Develops solutions that not only address biases but also promote responsible AI use in alignment with societal values and ethical standards, demonstrating a holistic understanding of AI's ethical dimensions.
4 pts
Very Good
Develops solutions that effectively address biases and promote responsible AI use, with clear consideration of societal values and ethical standards.
3 pts
Satisfactory
Develops solutions that address biases and promote responsible AI use to some extent, but with occasional gaps or inconsistencies in alignment with societal values and ethical standards.
2 pts
Fair
Develops solutions that partially address biases but lack clear alignment with societal values and ethical standards, showing limited consideration of responsible AI use.
1 pts
Poor
Fails to develop solutions or develops ineffective solutions that do not address biases or promote responsible AI use aligned with societal values and ethical standards.
5 pts

 This criterion is linked to a Learning Outcome
 Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 20
"""
             
             
         ),



         "M3 W1 Assignment: Unleashing AI for Informed Strategies": ( 
"""
Criteria	Ratings	Pts

 This criterion is linked to a Learning Outcome
 Evaluate the fundamental principles of Artificial Intelligence (AI) and Generative AI.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--
This criterion is linked to a Learning Outcome
Understanding of AI Principles:
5 pts
Excellent
Exceptional demonstration of a comprehensive understanding of AI principles, showcasing a deep grasp of fundamental concepts, terminology, and theories related to AI.
4 pts
Very Good
Strong understanding of AI principles, with clear and accurate explanations of key concepts, though some minor areas may require further elaboration.
3 pts
Satisfactory
Adequate understanding of basic AI principles, but with occasional inaccuracies or gaps in knowledge that need improvement.
2 pts
Fair
Limited understanding of AI principles, with significant inaccuracies or misconceptions evident in the explanation.
1 pts
Poor
Little to no understanding of AI principles, with numerous inaccuracies and fundamental misunderstandings apparent.
5 pts
This criterion is linked to a Learning OutcomeAnalysis of AI Use Cases
5 pts
Excellent
Exceptional analysis of two AI use cases, providing a thorough and insightful examination of how AI is applied in decision-making within the company.
4 pts
Very Good
Strong analysis of AI use cases, with a clear and well-structured presentation of relevant details, demonstrating a high level of critical thinking.
3 pts
Satisfactory
Adequate analysis of AI use cases, with some key details or connections between use cases and decision-making processes needing further elaboration.
2 pts
Fair
Limited analysis of AI use cases, with significant gaps or lack of clarity in explaining their relevance to decision-making.
1 pts
Poor
Minimal to no analysis of AI use cases, with a lack of understanding or effort to connect the use cases to decision-making principles.
5 pts

This criterion is linked to a Learning Outcome
Description of Data Requirements:
5 pts
Excellent
Exceptional articulation of the data needed for the selected AI use cases, demonstrating a clear understanding of data types, sources, and their significance in the context of decision-making.
4 pts
Very Good
Clear and accurate description of the data requirements, with a strong connection between the specified data and its role in supporting AI applications for decision-making.
3 pts
Satisfactory
Adequate description of data requirements, but with some vagueness or lack of detail in connecting specific data elements to the AI use cases.
2 pts
Fair
Limited description of data requirements, with notable gaps in understanding or lack of clarity on how the specified data supports the AI applications.
1 pts
Poor
Incomplete or inaccurate description of data requirements, with a lack of understanding of the essential data elements needed for the AI use cases
5 pts

This criterion is linked to a Learning Outcome
Justification of Algorithm Choice:
5 pts
Excellent
Convincing and well-supported justification for the chosen type of algorithm (supervised or unsupervised learning), demonstrating a deep understanding of the algorithm's suitability for the described use cases.
4 pts
Very Good
Sound justification for the algorithm choice, with clear reasoning and connections to the characteristics of the AI use cases and decision-making requirements.
3 pts
Satisfactory
Adequate justification for the algorithm choice, but with some areas where the rationale could be further developed or clarified.
2 pts
Fair
Limited or unclear justification for the chosen algorithm, with significant gaps in explaining its appropriateness for the specified AI use cases.
1 pts
Poor
Lack of justification or an incorrect rationale for the chosen algorithm, indicating a fundamental misunderstanding of the factors influencing the selection.
5 pts

 This criterion is linked to a Learning Outcome
 Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 20
"""
             
             
         ),






         "M2 W2 Assignment: Assessing Data Management and data governance in an Organization": ( 
"""
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Analyse the key principles of data management and governance for effective utilisation.
threshold: 3.0 pts
5 pts - Excellent
4 pts - Very Good
3 pts - Satisfactory
2 pts - Fair
1 pts - Poor

--

This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts - Assignment submitted before deadline expired
4 pts - Submitted max. two days after deadline expired
3 pts - Submitted three to seven days after deadline expired
2 pts - Submitted eight to fifteen days after deadline expired
1 pts - Submitted more than two weeks after deadline expired

--

This criterion is linked to a Learning Outcome
DMBOK Alignment:
5 pts - Excellent
   Thoroughly evaluates and demonstrates a deep understanding of how the organization's data management and governance 
   practices align with 2-3 selected domains from the DMBOK framework. Provides specific and well-supported examples of 
   alignment, showcasing comprehensive knowledge of DMBOK principles.
4 pts - Very Good
   Effectively evaluates the alignment of the organization's practices with the DMBOK framework, covering key aspects of 
   2-3 selected domains. Presents clear evidence of understanding DMBOK principles but may lack the depth seen in an 
   "Excellent" response.
3 pts - Satisfactory
   Provides a reasonable evaluation of the organization's practices in relation to the DMBOK framework. Identifies some 
   alignment points but may lack specificity or depth in the analysis.
2 pts - Fair
   Offers a basic assessment of DMBOK alignment with limited depth and specificity. Demonstrates a partial understanding 
   of DMBOK principles.
1 pts - Poor
   Fails to assess or inaccurately assesses the organization's alignment with DMBOK principles.

--

This criterion is linked to a Learning Outcome
Gap Analysis:
5 pts - Excellent
   Conducts a comprehensive and insightful gap analysis, identifying and thoroughly exploring areas where the organization 
   does not comply with DMBOK principles. Clearly distinguishes between current practices and desired DMBOK standards.
4 pts - Very Good
   Performs a solid gap analysis, pinpointing key areas where the organization falls short of DMBOK standards. Provides 
   detailed insights into identified gaps, though not as exhaustive as an "Excellent" response.
3 pts - Satisfactory
   Identifies some gaps in the organization's practices compared to DMBOK, but the analysis may lack depth or clarity.
2 pts - Fair
   Presents a basic gap analysis with limited insight into areas of non-compliance with DMBOK.
1 pts - Poor
   Fails to identify or inaccurately identifies gaps in the organization's adherence to DMBOK principles.

--

This criterion is linked to a Learning Outcome
Recommendations:
5 pts - Excellent
   Provides highly actionable and well-supported recommendations for the organization to align better with DMBOK best 
   practices. Demonstrates a nuanced understanding of the specific steps needed for improvement.
4 pts - Very Good
   Offers clear and practical recommendations for the organization to enhance alignment with DMBOK. May lack the depth 
   or specificity seen in an "Excellent" response.
3 pts - Satisfactory
   Presents reasonable recommendations, but they may be somewhat generic or lack specificity.
2 pts - Fair
   Provides basic recommendations that may lack detail or fail to address critical areas of improvement.
1 pts - Poor
   Fails to provide meaningful or relevant recommendations for the organization.


Total Points: 15
"""
             
             
         ),



         "M4 W2 Assignment: Application of Prompt Engineering Principles": ( 
"""
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome
Application of Principles in Prompt Engineering:
5 pts
Excellent
Applies prompt engineering principles exceptionally well, resulting in precise and desired outcomes.
4 pts
Very Good
Applies prompt engineering principles effectively with minor areas for refinement.
3 pts
Satisfactory
Applies prompt engineering principles adequately, with room for improvement in precision.
2 pts
Fair
Demonstrates limited application of prompt engineering principles, with notable shortcomings.
1 pts
Poor
Fails to apply prompt engineering principles effectively in obtaining desired outcomes.
5 pts

This criterion is linked to a Learning Outcome
Iterative Prompt Refinement:
5 pts
Excellent
Successfully iterates prompts, refining with each interaction to achieve the desired GenAI outcome.
4 pts
Very Good
Shows effective iterative prompt refinement with minor areas for enhancement.
3 pts
Satisfactory
Demonstrates basic iterative prompt refinement, with some missed opportunities for improvement.
2 pts
Fair
Limited ability to iteratively refine prompts, with significant gaps in the refinement process.
1 pts
Poor
Fails to iterate prompts effectively, resulting in a lack of progress toward the desired outcome.
5 pts

This criterion is linked to a Learning Outcome
Evaluate the fundamental principles of (Generative) Artificial Intelligence (GenAI).
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--
This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 10
"""
             
             
         ),





         "M5 W2 Assignment: Navigating Environmental and Societal Impacts of AI: A Sustainable Development Challenge": ( 
"""
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome
Analyse the potential social and environmental consequences of AI technologies within a business context, emphasising sustainability, corporate responsibility, and positive societal contributions.
threshold: 3.0 pts

5 pts - Excellent  
4 pts - Very Good  
3 pts - Satisfactory  
2 pts - Fair  
1 pts - Poor  

--

This criterion is linked to a Learning Outcome  
Analysis of Environmental and Societal Implications:  

5 pts - Excellent  
Demonstrates an exceptional understanding of the environmental and societal implications of AI, with comprehensive analysis and insightful evaluation. The analysis is deeply supported by specific examples and demonstrates a critical engagement with the complexities of sustainable AI development.  

4 pts - Very Good  
Provides a thorough analysis of environmental and societal implications, supported by relevant examples and insightful evaluation. While not as comprehensive as an excellent rating, the analysis demonstrates a solid understanding of sustainable AI development.  

3 pts - Satisfactory  
Shows a basic understanding of environmental and societal implications, with some analysis supported by examples. Indicates a moderate level of engagement with the topic and a general grasp of the challenges in sustainable AI development.  

2 pts - Fair  
Offers limited analysis of environmental and societal implications, with few examples or shallow evaluation. Shows some awareness of the assignment’s objectives but lacks depth or critical engagement.  

1 pts - Poor  
Displays minimal understanding of the environmental and societal implications, with scant analysis or insight. Examples are unsupported or irrelevant, showing a lack of engagement with the assignment’s objectives.  

5 pts  

This criterion is linked to a Learning Outcome  
Development of Sustainable AI Solutions:  

5 pts - Excellent  
Proposes innovative and well-reasoned AI solutions that effectively address identified environmental and societal challenges. Demonstrates a deep understanding of sustainability principles and their application in crafting responsible AI technologies.  

4 pts - Very Good  
Offers creative and feasible AI solutions for the challenges identified, effectively applying sustainability principles. While not as innovative as an excellent rating, solutions demonstrate a strong grasp of sustainable AI development.  

3 pts - Satisfactory  
Offers basic AI solutions for the challenges identified, applying sustainability principles to a certain extent. Solutions show understanding but lack depth, creativity, or a comprehensive approach to sustainability.  

2 pts - Fair  
Provides minimal or superficial AI solutions with little to no effective application of sustainability principles. Demonstrates a limited understanding of how to address environmental and societal challenges through AI.  

1 pts - Poor  
Presents inadequately developed AI solutions that fail to address the identified challenges or lack feasibility. Shows little understanding of sustainability principles in AI development.  

5 pts  

This criterion is linked to a Learning Outcome  
Integration of Ethical Principles in Solution Design:  

5 pts - Excellent  
Excellently integrates ethical principles such as fairness, transparency, and accountability into the AI solution, demonstrating a nuanced approach to ethical AI design and deployment.  

4 pts - Very Good  
Effectively integrates ethical principles into the AI solution, though the application may lack some depth or innovation. Demonstrates a strong commitment to ethical considerations in AI design.  

3 pts - Satisfactory  
Adequately integrates some ethical principles into the AI solution, though the application may lack depth or consistency. Shows a basic commitment to ethical considerations in AI development.  

2 pts - Fair  
Shows minimal or inconsistent integration of ethical principles in the AI solution, indicating a limited understanding of their importance in AI development and use.  

1 pts - Poor  
Fails to integrate ethical principles effectively into the AI solution, demonstrating a lack of understanding of their relevance and significance.  

5 pts  

Total Points: 15
"""
             
             
         ),





         "M5 W3 Assignment: Designing Effective AI Governance Frameworks": ( 
"""
Criteria	Ratings	Pts

 This criterion is linked to a Learning Outcome
 Interpret AI governance and regulatory frameworks, ensuring that AI-driven business practices comply with legal and ethical standards to minimise risks and promote responsible AI use.
threshold: 3.0 pts
5 pts
Excellent
4 pts
Very Good
3 pts
Satisfactory
2 pts
Fair
1 pts
Poor
--

This criterion is linked to a Learning Outcome
Analysis of Governance Challenges:
5 pts
Excellent
Provides a comprehensive and insightful analysis of AI governance challenges specific to the chosen industry, supported by detailed examples and demonstrating a deep understanding of the complexities involved in AI regulation and ethics.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Presents a basic understanding of governance challenges with some analysis supported by relevant examples. Shows engagement with the topic and an understanding of common issues in AI governance.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Offers minimal analysis of governance challenges, with little to no support from examples or relevant details. Shows a lack of engagement with the complexities of AI governance.
5 pts

This criterion is linked to a Learning Outcome
Development of AI Governance Framework:
5 pts
Excellent
Proposes a well-structured and innovative AI governance framework that effectively addresses the identified challenges. Demonstrates an advanced understanding of how to implement, monitor, and adapt governance mechanisms over time.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Proposes a basic AI governance framework that addresses some challenges identified. The framework is adequately thought out but lacks depth or a detailed approach to implementation and adaptation.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Provides a minimal or superficial governance framework with little to no effective strategy for addressing the governance challenges identified. Lacks understanding of how to develop a functional and adaptable governance framework.
5 pts

This criterion is linked to a Learning Outcome
Integration of Ethical Principles in Governance Design:
5 pts
Excellent
Excellently integrates ethical principles such as fairness, transparency, accountability, and stakeholder engagement into the governance framework, showing a nuanced and critical approach to ethical AI governance.
4 pts
Very Good
Between Excellent and Satisfactory
3 pts
Satisfactory
Adequately integrates some ethical principles into the governance framework, but the application may lack depth, innovation, or a holistic approach. Shows a commitment to ethical considerations but may not fully capture all necessary aspects.
2 pts
Fair
Between Satisfactory and Poor
1 pts
Poor
Shows minimal or incorrect integration of ethical principles in the governance framework, indicating a lack of understanding of the critical role of ethics in AI governance.
5 pts

 This criterion is linked to a Learning OutcomeTime Management
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--

Total Points: 15
"""
             
         ),
         
         
         
         
         
         
        "Week 1 Assignment: Software Requirements and Specifications": ( 
         
         """
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome
Time Management:  
threshold: 3.0 pts  
5 pts  
Assignment submitted before deadline expired  
4 pts  
Submitted max. two days after deadline expired  
3 pts  
Submitted three to seven days after deadline expired  
2 pts  
Submitted eight to fifteen days after deadline expired  
1 pts  
Submitted more than two weeks after deadline expired  
5 pts  


This criterion is linked to a Learning Outcome
Core Requirements:  
10 pts  
Clearly defined 5 core requirements  
8 pts  
Satisfactory requirements with some gaps  
6 pts  
Basic requirements with limited clarity  
4 pts  
Limited requirements  
2 pts  
Inadequate requirements  
10 pts  

This criterion is linked to a Learning Outcome
Project Overview:  
5 pts  
Thorough and comprehensive project overview provided  
4 pts  
Sufficient project overview, but some key details may be missing  
3 pts  
Basic project overview, lacking in-depth information  
2 pts  
Limited project overview with significant gaps in understanding  
1 pts  
Inadequate project overview  
5 pts  

This criterion is linked to a Learning Outcome
Specifications:  
10 pts  
Well-defined 5 specifications  
8 pts  
Satisfactory specifications with some gaps  
6 pts  
Basic specifications with limited details  
4 pts  
Limited specifications  
2 pts  
Inadequate specifications  
10 pts  



Total Points: 30
"""
        ),
         
         
         
         
         
         
        "Week 2 Assignment: Applying Agile Concepts to Project Management": ( 
         """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome: 
Time Management:
threshold: 3.0 pts
5 pts - Assignment submitted before deadline expired  
4 pts - Submitted max. two days after deadline expired  
3 pts - Submitted three to seven days after deadline expired  
2 pts - Submitted eight to fifteen days after deadline expired  
1 pts - Submitted more than two weeks after deadline expired  
Total: 5 pts

This criterion is linked to a Learning Outcome: 
Apply Agile concepts to project management:
10 pts - Excellent application of Agile principles with depth and clarity  
8 pts - Good application of Agile principles, but some areas could be improved  
6 pts - Adequate application of Agile principles, but lacking depth or clarity  
4 pts - Limited application of Agile principles with significant gaps  
2 pts - Inadequate application of Agile principles  
Total: 10 pts

This criterion is linked to a Learning Outcome: 
Project Overview:  
5 pts - Thorough and comprehensive project overview provided  
4 pts - Sufficient project overview, but some key details may be missing  
3 pts - Basic project overview, lacking in-depth information  
2 pts - Limited project overview with significant gaps in understanding  
1 pts - Inadequate project overview  
Total: 5 pts

This criterion is linked to a Learning Outcome: 
Applying Agile Principles:  
5 pts - Clear and well-developed explanation of applying Agile principles  
4 pts - Satisfactory explanation of applying Agile principles, but with some gaps or lack of clarity  
3 pts - Limited explanation of applying Agile principles with notable deficiencies  
2 pts - Incomplete or unclear explanation of applying Agile principles  
1 pts - Minimal or no attempt to apply Agile principles  
Total: 5 pts


Total Points: 25
"""
       ),
         
         
  "Week 3 Assignment: Design a Digital Product with User-Centered Design": (


    """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome: 
Time Management  
threshold: 3.0 pts  
5 pts - Assignment submitted before deadline expired  
4 pts - Submitted max. two days after deadline expired  
3 pts - Submitted three to seven days after deadline expired  
2 pts - Submitted eight to fifteen days after deadline expired  
1 pts - Submitted more than two weeks after deadline expired  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
User Persona:  
5 pts - Clear and well-developed user persona with detailed information  
4 pts - Satisfactory user persona, but some aspects could be further elaborated  
3 pts - Basic user persona with limited depth or clarity  
2 pts - Limited user persona with notable deficiencies in understanding  
1 pts - Inadequate user persona provided  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
User Story Mapping:  
10 pts - Thorough and comprehensive user story mapping with clear prioritization  
8 pts - Satisfactory user story mapping, but some aspects could be improved  
6 pts - Basic user story mapping with limited depth or clarity  
4 pts - Limited user story mapping with significant gaps  
2 pts - Inadequate user story mapping provided  
Total: 10 pts  


Total Points: 20
"""
),   
 
         
         
         
         
        "Week 4 Assignment: Scrum Methodology Key Takeaways": (  
             
         """
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome: 
Fictional Project Overview:
5 pts  - Clear and well-structured overview
4 pts  - Satisfactory overview
3 pts  - Basic overview
2 pts  - Limited overview
1 pts  - Inadequate overview provided
0 pts  - No overview provided

5 pts  

This criterion is linked to a Learning Outcome: 
Time Management:
threshold: 3.0 pts
5 pts  - Assignment submitted before deadline expired
4 pts  - Submitted max. two days after deadline expired
3 pts  - Submitted three to seven days after deadline expired
2 pts  - Submitted eight to fifteen days after deadline expired
1 pts  - Submitted more than two weeks after deadline expired

5 pts  

This criterion is linked to a Learning Outcome: 
Key Takeaways:
10 pts  - Identification and highlighting of key takeaways
8 pts   - Satisfactory identification and highlighting
6 pts   - Basic identification and highlighting
4 pts   - Limited identification and highlighting
2 pts   - Inadequate identification and highlighting provided
0 pts   - No identification and highlighting provided

10 pts  


Total Points: 20
"""
      ),
         
         
         
         
        
        
        
        "Week 5 Assignment: Lean Fundamentals": ( 
        """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome: 
Time Management:  
threshold: 3.0 pts  
5 pts - Assignment submitted before deadline expired  
4 pts - Submitted max. two days after deadline expired  
3 pts - Submitted three to seven days after deadline expired  
2 pts - Submitted eight to fifteen days after deadline expired  
1 pt - Submitted more than two weeks after deadline expired  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
Fictional Project Overview:  
5 pts - Clear and concise overview  
4 pts - Satisfactory overview  
3 pts - Basic overview  
2 pts - Limited overview  
1 pt - Inadequate overview provided  
0 pts - No overview provided  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
Waste Identification:  
5 pts - Identification of at least 3 examples of waste  
4 pts - Satisfactory identification of waste  
3 pts - Basic identification of waste  
2 pts - Limited identification of waste  
1 pt - Inadequate identification of waste provided  
0 pts - No identification of waste provided  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
Waste Reduction Strategies:  
10 pts - Proposed strategies for reducing waste  
8 pts - Satisfactory strategies proposed  
6 pts - Basic strategies proposed  
4 pts - Limited strategies proposed  
2 pts - Inadequate strategies proposed  
0 pts - No strategies proposed  
Total: 10 pts  



Total Points: 25  
"""
 
      ),     
         
         
         
         
         
         
        "Week 6 Assignment: Lean Startup": (  
         """
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome: 
Fictional Startup Overview:
5 pts  - Clear and concise project overview  
4 pts  - Satisfactory project overview  
3 pts  - Basic project overview  
2 pts  - Limited project overview  
1 pts  - Inadequate project overview provided  
0 pts  - No project overview provided  
5 pts  

This criterion is linked to a Learning Outcome: 
Time Management:  
threshold: 3.0 pts  
5 pts  - Assignment submitted before deadline expired  
4 pts  - Submitted max. two days after deadline expired  
3 pts  - Submitted three to seven days after deadline expired  
2 pts  - Submitted eight to fifteen days after deadline expired  
1 pts  - Submitted more than two weeks after deadline expired  
5 pts  

This criterion is linked to a Learning Outcome: 
Hypothesis:  
5 pts  - Clear and testable hypothesis  
4 pts  - Satisfactory hypothesis  
3 pts  - Basic hypothesis  
2 pts  - Limited hypothesis  
1 pts  - Inadequate hypothesis provided  
0 pts  - No hypothesis provided  
5 pts  

This criterion is linked to a Learning Outcome: 
Experiment:  
5 pts  - Well-described experiment  
4 pts  - Satisfactory experiment  
3 pts  - Basic experiment  
2 pts  - Limited experiment  
1 pts  - Inadequate experiment provided  
0 pts  - No experiment provided  
5 pts  

This criterion is linked to a Learning Outcome: 
Pivot:  
5 pts  - Clear and feasible pivot strategy  
4 pts  - Satisfactory pivot strategy  
3 pts  - Basic pivot strategy  
2 pts  - Limited pivot strategy  
1 pts  - Inadequate pivot strategy provided  
0 pts  - No pivot strategy provided  
5 pts  



Total Points: 25
"""

        ), 
         
         
         
         
         "Week 7 Assignment: Test and Deploy Quality Software": (  
         """
Criteria    Ratings    Pts

This criterion is linked to a Learning Outcome: 
Automated Static Analysis:  
10 pts - Perfectly functional analysis on push  
8 pts - Satisfactory analysis with minor issues  
6 pts - Basic analysis with noticeable issues  
4 pts - Limited analysis with significant issues  
2 pts - Inadequate analysis  
0 pts - No analysis performed  
10 pts  

This criterion is linked to a Learning Outcome: 
Time Management:  
Threshold: 3.0 pts  
5 pts - Assignment submitted before deadline expired  
4 pts - Submitted max. two days after deadline expired  
3 pts - Submitted three to seven days after deadline expired  
2 pts - Submitted eight to fifteen days after deadline expired  
1 pts - Submitted more than two weeks after deadline expired  

This criterion is linked to a Learning Outcome: 
Automated Testing:  
10 pts - Perfectly functional tests on push  
8 pts - Satisfactory tests with minor issues  
6 pts - Basic tests with noticeable issues  
4 pts - Limited tests with significant issues  
2 pts - Inadequate tests  
0 pts - No testing performed  
10 pts  



Total Points: 20
"""

         
       ),  
         
         
         
         
         
         
         "Week 8 Assignment: Design Thinking": (  
         
         """
Criteria	Ratings	Pts
This criterion is linked to a Learning Outcome
Problem Overview:
5 pts
- Clear and concise problem explanation
4 pts
- Satisfactory problem explanation
3 pts
- Basic problem explanation
2 pts
- Limited problem explanation
1 pts
- Inadequate problem explanation provided
0 pts
- No problem explanation provided
5 pts

This criterion is linked to a Learning Outcome
Ask "Why?" Five Times:
10 pts
- Comprehensive and specific analysis
8 pts
- Satisfactory analysis
6 pts
- Basic analysis
4 pts
- Limited analysis
2 pts
- Inadequate analysis provided
0 pts
- No analysis provided
10 pts

This criterion is linked to a Learning Outcome
Document the Analysis:
5 pts
- Thorough documentation with evidence
4 pts
- Satisfactory documentation
3 pts
- Basic documentation
2 pts
- Limited documentation
1 pts
- Inadequate documentation provided
0 pts
- No documentation provided
5 pts

This criterion is linked to a Learning Outcome
Identify the Root Causes:
5 pts
- Comprehensive list of root causes
4 pts
- Satisfactory list of root causes
3 pts
- Basic list of root causes
2 pts
- Limited list of root causes
1 pts
- Inadequate list of root causes provided
0 pts
- No list of root causes provided
5 pts

This criterion is linked to a Learning Outcome
Proposed Solutions:
5 pts
- Well-defined and effective solutions
4 pts
- Satisfactory solutions proposed
3 pts
- Basic solutions proposed
2 pts
- Limited solutions proposed
1 pts
- Inadequate solutions proposed
0 pts
- No solutions proposed
5 pts

This criterion is linked to a Learning Outcome
Time Management:
threshold: 3.0 pts
5 pts
Assignment submitted before deadline expired
4 pts
Submitted max. two days after deadline expired
3 pts
Submitted three to seven days after deadline expired
2 pts
Submitted eight to fifteen days after deadline expired
1 pts
Submitted more than two weeks after deadline expired
--



Total Points: 30
"""

      )   
         
         
         
         
         
         
         
         
         
         
         
         
    
    }
    return rubrics.get(assignment_name, 
                       
   """
Criteria	Ratings	Pts

This criterion is linked to a Learning Outcome: 
Time Management  
threshold: 3.0 pts  
5 pts - Assignment submitted before deadline expired  
4 pts - Submitted max. two days after deadline expired  
3 pts - Submitted three to seven days after deadline expired  
2 pts - Submitted eight to fifteen days after deadline expired  
1 pts - Submitted more than two weeks after deadline expired  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
User Persona:  
5 pts - Clear and well-developed user persona with detailed information  
4 pts - Satisfactory user persona, but some aspects could be further elaborated  
3 pts - Basic user persona with limited depth or clarity  
2 pts - Limited user persona with notable deficiencies in understanding  
1 pts - Inadequate user persona provided  
Total: 5 pts  

This criterion is linked to a Learning Outcome: 
User Story Mapping:  
10 pts - Thorough and comprehensive user story mapping with clear prioritization  
8 pts - Satisfactory user story mapping, but some aspects could be improved  
6 pts - Basic user story mapping with limited depth or clarity  
4 pts - Limited user story mapping with significant gaps  
2 pts - Inadequate user story mapping provided  
Total: 10 pts  


Total Points: 20
"""
)






           
