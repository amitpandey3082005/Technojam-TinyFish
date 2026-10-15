import os
import streamlit as str_ui
from dotenv import load_dotenv
from tinyfish import TinyFish

# 1. Environment variables load karein (.env file se)
load_dotenv()

# 2. TinyFish Client initialize karein
try:
    client = TinyFish()
except Exception as e:
    str_ui.error(f"❌ Client initialization failed. Check your .env file: {e}")

# 3. Backend Function (Search, Filters, and URL display structure)
def find_and_extract_jobs(role, location, skills, limit_val):
    # Dynamic Search Query: Isme ab Skills bhi embedded hain behtar search index ke liye
    query = f"site:://linkedin.com OR site:://indeed.com {role} {skills} jobs in {location}"
    
    str_ui.info(f"🔍 Searching TinyFish for jobs matching your criteria...")
    
    try:
        # SDK query call (Bina limit parameter ke taaki TypeError na aaye)
        search_results = client.search.query(query=query)
        
        if not search_results or not search_results.results:
            str_ui.warning("❌ Aapke filters ke mutabik koi job posting nahi mili. Kripya keywords badlein.")
            return

        str_ui.success(f"🎉 Humne top job postings dhoond li hain! Niche dekhein:")
        str_ui.markdown("---")

        # Loop through results using object slicing
        for index, job in enumerate(search_results.results[:limit_val]):
            job_url = job.url      
            job_title = job.title  
            
            # Clean and Highly Scannable UI Container
            with str_ui.container():
                # Job Title Block
                str_ui.markdown(f"### 📌 {index + 1}. {job_title}")
                
                # Highlighted URL Block (Sare URL properly dikhane ke liye metric/code style)
                str_ui.markdown("**🔗 Source Job Link (Click to Apply):**")
                str_ui.code(job_url, language="markdown")
                str_ui.markdown(f"[ Go to Job Post]({job_url})")
                
                # Fetching Details Spinner
                with str_ui.status(" Extracting full job requirements...", expanded=False) as status:
                    try:
                        fetched_data = client.fetch.url(
                            url=job_url,
                            purpose=f"Extract Job Title, Company Name, Salary, and check if it matches required skills: {skills}."
                        )
                        
                        if fetched_data and fetched_data.get('content'):
                            str_ui.markdown(fetched_data.get('content'))
                            status.update(label="Details Extracted Successfully!", state="complete")
                        else:
                            str_ui.write(" Is page se content extract nahi ho paya.")
                            status.update(label="Extraction Failed", state="error")
                            
                    except Exception as fetch_err:
                        str_ui.error(f" Detail fetch error: {fetch_err}")
                        status.update(label="Error Occurred", state="error")
                
                # Visual Divider between multiple jobs
                str_ui.markdown("<br><hr style='border-top: 1px dashed #bbb;'>", unsafe_allow_html=True)
                    
    except Exception as search_err:
        str_ui.error(f" Search request fail ho gayi: {search_err}")

# 4. Streamlit Frontend Layout Configuration
def main():
    str_ui.set_page_config(page_title="TinyFish Advanced Job Finder", page_icon="💼", layout="wide")
    
    # Title aur Subtitle
    str_ui.title("💼 TinyFish Advanced Job Portal Finder")
    str_ui.write("Job Finder portal ")
    str_ui.markdown("---")
    
    # Sidebar Filters Panel (Isme ab teeno filters hain)
    str_ui.sidebar.header(" Filter Options")
    
    user_role = str_ui.sidebar.text_input("Preferred Role:", value="Python Developer")
    user_location = str_ui.sidebar.text_input("Preferred Location:", value="Remote")
    user_skills = str_ui.sidebar.text_input("Required Skills (e.g. Django, AWS, Pandas):", value="Django")
    
    # Result count slider
    max_results = str_ui.sidebar.slider("How many jobs to show?", min_value=1, max_value=10, value=3)
    
    search_btn = str_ui.sidebar.button("Search Jobs 🚀", use_container_width=True)
    
    # Trigger application logic on button click
    if search_btn:
        if not user_role or not user_location:
            str_ui.sidebar.error("⚠️ Role aur Location daalna zaroori hai!")
        else:
            find_and_extract_jobs(
                role=user_role, 
                location=user_location, 
                skills=user_skills, 
                limit_val=max_results
            )

if __name__ == "__main__":
    main()
