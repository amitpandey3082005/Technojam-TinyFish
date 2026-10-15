import os
import streamlit as str_ui
from dotenv import load_dotenv
from tinyfish import TinyFish

# 1. Environment configuration setup
load_dotenv()

# Strict authentication check
api_key = os.getenv("TINYFISH_API_KEY")

if not api_key:
    str_ui.error("❌ Setup Error: TINYFISH_API_KEY was not located in your .env file.")
else:
    print(f"[SYSTEM NOTICE]: Initializing Agent instance with token profile: {api_key[:15]}...")

# Initialize the official TinyFish client session context
try:
    client = TinyFish()
except Exception as e:
    str_ui.error(f"❌ Failed to boot TinyFish client interface: {e}")

# 2. Premium Paid Agent Scraping Pipeline Routine
def execute_premium_agent_scrape(role, location, skills, max_jobs):
    # Constructing a generic web query (Free layer node discovery)
    search_query = f'"{role}" "{skills}" vacancies in "{location}"'
    str_ui.info("🌐 Phase 1: Scanning web index maps for target links...")
    
    try:
        search_data = client.search.query(query=search_query)
        
        if not search_data or not search_data.results:
            str_ui.warning("❌ No open web career tracks located for these filters.")
            return
            
        str_ui.success(f"🎉 Links mapped successfully! Initializing paid virtual browser agent streams...")
        str_ui.markdown("---")
        
        # Slicing the target job dataset arrays
        for idx, job in enumerate(search_data.results[:max_jobs]):
            target_url = job.url
            target_title = job.title
            
            with str_ui.container():
                str_ui.markdown(f"### 📌 {idx + 1}. {target_title}")
                str_ui.code(target_url, language="markdown")
                
                # LAUNCHING PREMIUM CLOUD SESSION (THIS PROCESS REDUCES WALLET CREDITS)
                with str_ui.status("🤖 Spawning paid virtual headless node for content extraction...", expanded=False) as status:
                    try:
                        # Correct official paid action sequence to instantiate cloud nodes
                        session = client.agent.create_session(
                            url=target_url,
                            instructions=f"Analyze this target job layout map. Isolate and summarize the role profile details, estimated corporate compensation structures, and core prerequisite skill tags matching: {skills}."
                        )
                        
                        # Displaying response text from the interactive session object
                        if session and hasattr(session, 'result'):
                            str_ui.markdown(session.result)
                            status.update(label="Cloud Browser Session evaluation complete!", state="complete")
                        else:
                            str_ui.write("⚠️ Target data window rendered empty or returned no visual blocks.")
                            status.update(label="Session processed an empty framework matrix", state="error")
                            
                    except Exception as node_err:
                        str_ui.error(f"⚠️ Node streaming error: {node_err}")
                        status.update(label="Paid processing loop crashed", state="error")
                
                str_ui.markdown("<br><hr style='border-top: 1px dashed #bbb;'>", unsafe_allow_html=True)
                
    except Exception as search_err:
        str_ui.error(f"💥 Web indexing pipeline process crash: {search_err}")

# 3. Streamlit Interface configuration
def main():
    str_ui.set_page_config(page_title="TinyFish Scratch Agent Finder", page_icon="💼", layout="wide")
    
    str_ui.title("💼 TinyFish Scratch AI Agent Job Finder")
    str_ui.write("A completely rewritten system using live billing components to fetch cross-platform data structures.")
    str_ui.markdown("---")
    
    # Input Dashboard layout fields configuration
    str_ui.sidebar.header("🎯 Agent System Configuration")
    
    role_input = str_ui.sidebar.text_input("Job Profile Designation:", value="Python Developer")
    location_input = str_ui.sidebar.text_input("Regional Boundary / Location:", value="Remote")
    skills_input = str_ui.sidebar.text_input("Core Toolkit Frameworks:", value="Django")
    
    job_depth = str_ui.sidebar.slider("Maximum continuous browser threads:", min_value=1, max_value=5, value=2)
    
    trigger_execution = str_ui.sidebar.button("Execute Paid Browser Matrix 🚀", use_container_width=True)
    
    if trigger_execution:
        if not role_input or not location_input:
            str_ui.sidebar.error("⚠️ Input Validation Fault: Core parameters cannot be left blank.")
        else:
            execute_premium_agent_scrape(
                role=role_input,
                location=location_input,
                skills=skills_input,
                max_jobs=job_depth
            )

if __name__ == "__main__":
    main()
